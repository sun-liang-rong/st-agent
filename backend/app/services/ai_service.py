"""AI 服务模块"""
import httpx
import json
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()


class AIService:
    """AI 服务类"""
    
    def __init__(self):
        self.api_key = settings.SENSENOVA_API_KEY
        self.api_base = settings.SENSENOVA_API_BASE
        self.prompt_model = settings.SENSENOVA_PROMPT_MODEL
        self.image_model = settings.SENSENOVA_IMAGE_MODEL
    
    async def analyze_file_and_generate_prompt(
        self, 
        file_data: str, 
        user_prompt: str,
        file_name: str = "data.xlsx"
    ) -> str:
        """
        分析文件并生成提示词
        使用 sensenova-6.7-flash-lite 模型
        """
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """你是一个数据可视化专家。用户会提供完整的 Excel 数据文件内容（**全部行和列**，不是抽样），你需要深入分析所有数据后生成一段**中文提示词**，用于 AI 图片生成模型绘制数据看板。

## 第一步：深入分析全部数据
接收到的数据是完整的，请遍历所有行和列进行全面分析：
- 总行数、总列数、每列的数据类型（数值/文本/日期/分类）
- 每列数值的统计特征：最小值、最大值、均值、中位数、总和、异常值
- 数据分布：各分类的占比、数值分布区间、是否有缺失值
- 趋势和模式：时间序列趋势、周期性、相关性、分组对比
- 关键发现：数据中最值得关注的 3-5 个核心洞察

## 第二步：生成提示词
基于分析结果，生成包含以下内容的中文提示词：

1. **图表类型**：根据数据特点推荐（柱状图对比、折线图趋势、饼图占比、散点图分布、或组合仪表盘）
2. **数据映射**：具体说明哪些数据项对应图表的哪些元素（如"将日期列映射到X轴，销售额映射到Y轴，用不同颜色区分产品类别"）
3. **配色方案**：用中文颜色名（深蓝色、翡翠绿、琥珀色、玫瑰红、紫色、橙色），**不要十六进制色号**
4. **布局风格**：现代简约、浅色背景、商务专业

## ⚠️ 文字规则（重要！）
- 提示词用中文写
- **不要使用十六进制色号（如 #1a56db）**
- **Y轴必须显示数字刻度**（如 0, 50, 100, 150...），让读者知道具体数值
- **禁止在图表中出现中文文字**（中文会渲染成乱码）
- 标题、图例、分类标签如需文字，用简短**英文**（如 "Sales", "2024", "Product A/B/C", "Q1-Q4"）
- 坐标轴标签文字保持简洁清晰
- 数字标注用阿拉伯数字,字体清晰易读"""
        
        data = {
            "model": self.prompt_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"文件名: {file_name}\n\n用户需求: {user_prompt}\n\n完整数据（全部行和列）:\n{file_data}\n\n这是完整的全部数据，请逐行逐列全面分析统计特征、趋势、分布和关键洞察，然后生成一段中文提示词。要求：Y轴显示数字刻度（0, 50, 100...）；分类标签和图例用简短英文（如 Product A, 2024, Q1）；禁止出现中文文字；整体风格现代商务。"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API 返回格式错误: {result}")
    
    async def generate_image(self, prompt: str) -> str:
        """
        根据提示词生成图像
        使用 sensenova-u1-fast 模型
        """
        url = f"{self.api_base}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 强化提示词：保证数字清𥇦，禁止中文文字
        enhanced_prompt = (
            "专业的数据图表可视化，现代商务风格，浅色干净背景，"
            "平滑质感，高分辨率，8K画质。\n\n"
            f"{prompt}\n\n"
            "REQUIRED: Show numeric labels on the Y-axis (e.g., 0, 50, 100, 150) with clean readable digits. "
            "Use short English words for title, legend, and category labels if needed. "
            "No Chinese characters anywhere — they will become garbled. "
            "No hex color codes. Use simple color names."
        )
        
        data = {
            "model": self.image_model,
            "prompt": enhanced_prompt,
            "n": 1,
            "size": "2752x1536"
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0].get("url", "")
            else:
                raise Exception(f"API 返回格式错误: {result}")


aiservice = AIService()
