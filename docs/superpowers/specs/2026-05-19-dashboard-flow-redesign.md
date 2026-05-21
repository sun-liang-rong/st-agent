# 数据看板生成流程重设计

## 背景

当前系统使用 AI 图像生成模型（SenseNova U1 Fast）来"画"数据图表。由于图像模型只能根据文字描述生成图片，无法精确渲染数据值，导致生成的图表数字不准确、标签错误、比例失真。

## 目标

将图表生成方式从"AI 画图"改为"AI 生成 ECharts 配置 + 前端精确渲染"，确保用户看到的图表完全基于真实数据。

## 技术选型

| 项目 | 选择 | 理由 |
|------|------|------|
| 图表库 | ECharts + vue-echarts | 功能全面，中文生态好，图表类型丰富 |
| AI 输出格式 | ECharts JSON 配置 | 可直接 setOption 渲染，格式固定不易出错 |
| 看板布局 | AI 指定 size + 前端网格渲染 | AI 理解数据重要性，前端控制响应式 |

## 新流程

```
阶段1:
  用户上传 Excel
    ↓
  后端读取数据（结构化列信息 + 数据样本）
    ↓
  文本模型分析数据 → 输出看板规格 JSON
    ↓
  返回给前端，用户可预览/编辑 JSON

阶段2:
  用户确认看板规格
    ↓
  前端用 ECharts 渲染完整看板
    ↓
  用户可交互（后续迭代）
```

## AI 输出规格

AI 必须输出以下 JSON 结构：

```json
{
  "title": "2024年销售数据看板",
  "description": "基于各地区、各产品线的销售数据分析",
  "charts": [
    {
      "id": "chart-1",
      "title": "月度销售趋势",
      "type": "line",
      "size": "full",
      "option": {
        "xAxis": { "type": "category", "data": ["1月", "2月", "3月"] },
        "yAxis": { "type": "value" },
        "series": [{ "data": [120, 200, 150], "type": "line" }]
      }
    },
    {
      "id": "chart-2",
      "title": "地区销售占比",
      "type": "pie",
      "size": "half",
      "option": {
        "series": [{
          "type": "pie",
          "data": [
            { "value": 335, "name": "华东" },
            { "value": 210, "name": "华南" }
          ]
        }]
      }
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 看板标题 |
| `description` | string | 看板描述 |
| `charts` | array | 图表数组 |
| `charts[].id` | string | 唯一标识 |
| `charts[].title` | string | 图表标题 |
| `charts[].type` | string | 图表类型：line/bar/pie/scatter/radar/funnel/kline |
| `charts[].size` | string | 布局大小：full/half/third |
| `charts[].option` | object | 标准 ECharts option，可直接 setOption 渲染 |

### 布局规则

- `full`：独占一行，适合趋势图、大型图表
- `half`：占半行，适合饼图、中型柱状图
- `third`：占 1/3 行，适合 KPI 卡片、小型统计图
- 移动端统一单列堆叠

### AI Prompt 要点

- 输出必须是合法 JSON
- `option` 必须是标准 ECharts option，可直接渲染
- 数据值必须来自原始数据，禁止编造
- 中文分类名保留原文
- 颜色用 ECharts 内置主题或标准色值
- `size` 根据图表重要性和类型自动决定

## 后端改动

### ai_service.py

**删除：**
- `generate_image()` 方法
- `_download_and_save_image()` 方法

**新增/改造：**

```python
async def generate_dashboard_spec(
    self,
    file_data: str,
    user_prompt: str,
    file_name: str,
    selected_columns: list[str] | None,
    chart_type: str | None,
    chart_title: str | None,
) -> dict:
```

- System Prompt 改为要求输出看板 JSON
- 返回 dict 而非 str
- 内置 `validate_dashboard_spec()` 校验输出格式

### generate.py

**阶段1 改造 — 响应格式：**

```json
{
  "taskId": "uuid",
  "status": "spec_ready",
  "dashboardSpec": {
    "title": "...",
    "charts": [...]
  }
}
```

**阶段2 改造 — 新端点：**

`POST /{task_id}/confirm`

请求体：
```json
{
  "dashboardSpec": { "title": "...", "charts": [...] }
}
```

- 不再调用 AI 图像模型
- 保存用户编辑后的 `dashboard_spec` 到历史记录
- 返回确认成功

**删除：**
- `ImageGenerateRequest` 模型
- `generate_image_from_prompt()` 端点

### upload.py

**`suggest` 接口 prompt 改造：**

改为建议用户"可以生成哪些图表"，而非"生成什么图像 prompt"。例如：
> "数据包含'地区'（分类）和'销售额'（数值）两列，建议生成：1. 各地区销售额对比柱状图；2. 地区占比饼图；3. 月度趋势折线图（如有日期列）"

数据传递改为结构化列信息（已有基础，微调即可）

### 数据传递优化

大数据集不再 `df.to_string()`，改为结构化摘要：

```python
{
    "columns": [
        {"name": "销售额", "type": "numeric", "min": 100, "max": 5000, "mean": 1200},
        {"name": "地区", "type": "category", "values": ["华东", "华南", "华北", "西部"]}
    ],
    "sample_rows": [...前50行...],
    "total_rows": 10000
}
```

### main.py

- 删除 `generated/` 静态文件挂载（不再需要）

### config.py

- 删除 SenseNova 图像模型相关配置（`SENSENOVA_IMAGE_MODEL`）
- 保留文本模型配置

## 前端改动

### 新增依赖

```json
{
  "echarts": "^5.5.0",
  "vue-echarts": "^7.0.0"
}
```

### 新增组件

**DashboardRenderer.vue**
- 接收 `dashboard_spec` 对象
- 根据 `size` 字段排列网格布局
- 用 ECharts 渲染每个图表
- 响应式：桌面端网格，移动端单列
- 单个图表渲染失败不影响其他图表

**ChartCard.vue**
- 单个图表卡片容器
- 渲染 ECharts 图表
- 显示图表标题
- 错误处理：渲染失败显示错误提示 + 原始 JSON

**JsonEditor.vue（可选）**
- JSON 编辑器，用于用户编辑看板规格
- 实时校验 JSON 格式
- debounce 300ms 避免频繁渲染

### 改造 Home.vue

**阶段1：**
- 展示 AI 生成的看板 JSON
- 用 DashboardRenderer 实时预览
- 用户可编辑 JSON

**阶段2：**
- 不再调用后端生成图片
- 直接用 DashboardRenderer 渲染看板
- 用户确认后保存到历史记录

**消息类型扩展：**

```typescript
interface DashboardChart {
  id: string
  title: string
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'radar' | 'funnel' | 'kline'
  size: 'full' | 'half' | 'third'
  option: EChartsOption
}

interface DashboardSpec {
  title: string
  description?: string
  charts: DashboardChart[]
}

interface Message {
  // ...现有字段
  dashboardSpec?: DashboardSpec  // 新增：看板规格
  imageUrl?: string              // 保留字段，但新流程不再使用
}
```

### 改造 ReportConfig.vue

- 从"输入 prompt"改为"配置看板"
- 展示看板预览 + JSON 编辑

### 改造 History.vue

- 历史记录存储 `dashboard_spec` 而非 `image_url`
- 查看历史时用 DashboardRenderer 重新渲染

### 改造 api.ts

```typescript
// 删除
generateImage(taskId, prompt)

// 新增
confirmDashboard(taskId, dashboardSpec)
```

### 文件结构变化

```
src/components/
├── DashboardRenderer.vue   ← 新增
├── ChartCard.vue           ← 新增
├── JsonEditor.vue          ← 新增（可选）
├── DataPreview.vue         ← 保留
├── ReportConfig.vue        ← 改造
└── ...
```

## 异常处理

### AI 输出格式校验

```python
def validate_dashboard_spec(spec: dict) -> bool:
    # 必须有 title 和 charts
    # charts 必须是非空数组
    # 每个 chart 必须有 id, title, type, option
    # type 必须是合法的 ECharts 图表类型
    # size 必须是 full/half/third 之一
    # option 必须包含 series
```

- 第一次失败 → 自动重试，prompt 强调输出格式
- 第二次失败 → 返回错误，提示用户修改需求重试

### 前端渲染异常

- 每个 ChartCard 独立 try-catch
- 单个图表渲染失败不影响其他图表
- 失败图表显示错误提示 + 原始 JSON

### JSON 编辑实时预览

- 用户编辑 JSON → 实时校验 → 合法则重新渲染
- 非法 JSON → 显示错误位置，保留上次合法渲染
- debounce 300ms

## 删除清单

### 后端
- `ai_service.py`：`generate_image()`, `_download_and_save_image()`
- `generate.py`：`ImageGenerateRequest`, `generate_image_from_prompt()`
- `main.py`：`generated/` 静态文件挂载
- `config.py`：`SENSENOVA_IMAGE_MODEL`

### 前端
- `api.ts`：`generateImage()` 方法
- 相关的图片预览、下载逻辑（可选保留用于导出功能）

## 后续迭代（V2）

- 交互式看板编辑：用户在看板界面直接切换图表类型、筛选数据维度
- 看板导出：将 ECharts 图表导出为 PNG/PDF
- U1 Fast 集成（可选）：为看板生成装饰性封面
