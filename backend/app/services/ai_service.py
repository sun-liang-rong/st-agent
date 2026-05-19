"""AI 服务模块"""
import httpx
import json
from typing import Optional
from app.config import get_settings

settings = get_settings()

VALID_CHART_TYPES = {"line", "bar", "pie", "scatter", "radar", "funnel", "kline", "heatmap", "treemap"}
VALID_SIZES = {"full", "half", "third"}


def validate_dashboard_spec(spec: dict) -> tuple[bool, str]:
    """校验看板规格 JSON 格式，返回 (是否合法, 错误信息)"""
    if not isinstance(spec, dict):
        return False, "输出不是 JSON 对象"

    if "title" not in spec or not isinstance(spec["title"], str):
        return False, "缺少 title 字段或类型错误"

    if "charts" not in spec or not isinstance(spec["charts"], list):
        return False, "缺少 charts 字段或不是数组"

    if len(spec["charts"]) == 0:
        return False, "charts 数组为空"

    for i, chart in enumerate(spec["charts"]):
        prefix = f"charts[{i}]"
        if not isinstance(chart, dict):
            return False, f"{prefix} 不是对象"

        for field in ("id", "title", "type", "option"):
            if field not in chart:
                return False, f"{prefix} 缺少 {field} 字段"

        if chart["type"] not in VALID_CHART_TYPES:
            return False, f"{prefix}.type '{chart['type']}' 不是合法的图表类型，允许: {VALID_CHART_TYPES}"

        if "size" in chart and chart["size"] not in VALID_SIZES:
            return False, f"{prefix}.size '{chart['size']}' 不合法，允许: {VALID_SIZES}"

        if not isinstance(chart["option"], dict):
            return False, f"{prefix}.option 不是对象"

        if "series" not in chart["option"]:
            return False, f"{prefix}.option 缺少 series 字段"

    return True, ""


class AIService:
    """AI 服务类"""

    def __init__(self):
        self.api_key = settings.SENSENOVA_API_KEY
        self.api_base = settings.SENSENOVA_API_BASE
        self.prompt_model = settings.SENSENOVA_PROMPT_MODEL

    async def generate_dashboard_spec(
        self,
        file_data: str,
        user_prompt: str,
        file_name: str = "data.xlsx",
        selected_columns: list[str] | None = None,
        chart_type: str | None = None,
        chart_title: str | None = None,
    ) -> dict:
        """
        分析数据并生成看板规格 JSON
        返回合法的 DashboardSpec dict
        """
        # 构建用户偏好描述
        user_prefs = []
        if selected_columns:
            user_prefs.append(f"重点关注以下列: {', '.join(selected_columns)}")
        if chart_type:
            user_prefs.append(f"用户希望的图表类型: {chart_type}")
        if chart_title:
            user_prefs.append(f"用户指定的看板标题: {chart_title}")
        user_prefs_text = "\n".join(user_prefs) if user_prefs else ""

        system_prompt = f"""你是一个数据可视化专家。用户会提供 Excel 数据，你需要分析数据并生成一个数据看板的 ECharts 配置。

{'## 用户偏好\n' + user_prefs_text + '\n' if user_prefs_text else ''}
## 输出要求

你必须输出一个合法的 JSON 对象，格式如下：

```json
{{
  "title": "看板标题",
  "description": "简短描述",
  "charts": [
    {{
      "id": "chart-1",
      "title": "图表标题",
      "type": "line",
      "size": "full",
      "option": {{
        // 标准 ECharts option
        "xAxis": {{ "type": "category", "data": [...] }},
        "yAxis": {{ "type": "value" }},
        "series": [{{ "data": [...], "type": "line" }}]
      }}
    }}
  ]
}}
```

## 规则

1. 输出必须是合法 JSON，不要包含任何其他文字、代码块标记或解释
2. 每个 chart 的 option 必须是标准 ECharts option，可直接用 echarts.setOption(option) 渲染
3. 数据值必须来自原始数据，禁止编造数字
4. 中文分类名保留原文（如"华东"、"产品A"）
5. charts 数组至少包含 2 个图表，最多 6 个
6. type 合法值: line, bar, pie, scatter, radar, funnel, kline, heatmap, treemap
7. size 合法值: full（独占一行）, half（占半行）, third（占1/3行）
8. 趋势类图表用 full，占比类用 half，统计卡片用 third
9. 颜色使用 ECharts 默认主题色或标准 CSS 颜色名
10. 如果用户指定了标题，必须使用用户指定的标题

## 图表类型选择指南

- 时间序列/趋势 → line (full)
- 分类对比 → bar (full 或 half)
- 占比分布 → pie (half)
- 两变量关系 → scatter (half)
- 多维对比 → radar (half)
- 漏斗分析 → funnel (half)
- KPI 指标 → 使用 bar/line 配合特殊样式 (third)"""

        data = {
            "model": self.prompt_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"文件名: {file_name}\n\n用户需求: {user_prompt}\n\n数据:\n{file_data}"},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
        }

        # 最多重试 2 次
        last_error = ""
        for attempt in range(2):
            async with httpx.AsyncClient(timeout=120.0, proxy=None) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=data,
                )
                response.raise_for_status()
                result = response.json()

            if "choices" not in result or len(result["choices"]) == 0:
                raise Exception(f"API 返回格式错误: {result}")

            content = result["choices"][0]["message"]["content"].strip()

            # 尝试提取 JSON（处理 AI 可能包裹 ```json ``` 的情况）
            if content.startswith("```"):
                lines = content.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith("```") and not in_block:
                        in_block = True
                        continue
                    elif line.strip() == "```" and in_block:
                        break
                    elif in_block:
                        json_lines.append(line)
                content = "\n".join(json_lines)

            try:
                spec = json.loads(content)
            except json.JSONDecodeError as e:
                last_error = f"AI 输出不是合法 JSON: {e}"
                # 重试时强调输出格式
                data["messages"].append({"role": "assistant", "content": content})
                data["messages"].append({"role": "user", "content": "你的输出不是合法 JSON。请只输出 JSON 对象，不要包含其他文字。重新生成。"})
                continue

            valid, err = validate_dashboard_spec(spec)
            if not valid:
                last_error = f"看板规格校验失败: {err}"
                data["messages"].append({"role": "assistant", "content": content})
                data["messages"].append({"role": "user", "content": f"格式错误: {err}。请修正后重新输出合法的 JSON。"})
                continue

            return spec

        raise Exception(f"AI 生成看板规格失败（已重试2次）: {last_error}")


aiservice = AIService()
