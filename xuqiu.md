# ST-Agent 项目需求文档

## 一、项目概述

ST-Agent 是一个 **AI 旅游攻略与图片生成平台**，用户可通过对话形式与 AI 交互，获取旅游攻略文本，并生成对应风格的旅行图片。

### 核心定位
- 对话式旅游攻略生成（类似豆包/ChatGPT 的交互体验）
- AI 图片创作（支持多种风格和比例）
- 会话历史管理与多会话切换

### AI 模型
| 用途 | 模型 | API |
|------|------|-----|
| 对话 / 攻略生成 | `sensenova-6.7-flash-lite` | SenseNova Chat Completions |
| 图片生成 | `sensenova-u1-fast` | SenseNova Images Generate (OpenAI SDK 兼容) |

API 文档：https://platform.sensenova.cn/docs

---

## 二、技术架构

### 后端
- **框架**：FastAPI (Python)
- **数据库**：MySQL (SQLAlchemy ORM)
- **认证**：JWT (HS256, 30分钟过期)
- **流式响应**：SSE (Server-Sent Events)
- **图片存储**：本地 `generated/` 目录，通过 `/generated/` 静态路由访问

### 前端
- **框架**：Vue 3 + TypeScript + Pinia
- **构建**：Vite 7
- **样式**：TailwindCSS 3.4（amber/orange 暖色系设计语言）
- **HTTP**：Axios (REST) + fetch (SSE 流式)
- **Markdown**：marked + DOMPurify
- **国际化**：zh-CN / en 简易 i18n

### 代理配置
- `/api` → `http://localhost:8000/api/v1`
- `/generated` → `http://localhost:8000/generated`

---

## 三、功能模块

### 3.1 用户认证

#### 登录页 (`/login`)
- 用户名 + 密码登录
- 记住登录状态 checkbox
- 登录失败显示错误提示卡片
- 登录成功跳转 `/app`
- 底部跳转注册页链接

#### 注册页 (`/register`)
- 用户名 + 邮箱 + 密码 + 确认密码
- 密码不一致校验
- 注册成功自动跳转登录页
- 底部跳转登录页链接

#### 认证流程
- JWT Bearer Token 认证
- Token 存储在 localStorage
- 所有 API 请求自动注入 Authorization header
- 401 响应自动清除 token 并跳转 `/login`
- 支持 OAuth2 兼容登录接口

#### API 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录，返回 JWT |
| POST | `/api/v1/auth/login/oauth2` | OAuth2 兼容登录 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |

---

### 3.2 AI 对话（核心功能）

#### 对话页 (`/app` - Home.vue)

**界面布局**：
- 顶部：消息列表区域（可滚动）
- 底部：输入框区域

**空状态**：
- 居中展示欢迎语 "你好呀！想探索哪里？"
- 3 个快捷按钮：杭州三日游 / 成都美食之旅 / 云南自驾游

**消息气泡**：
- AI 消息：左侧头像 🤖 + 白色圆角气泡 + Markdown 渲染 + 流式打字光标 ▊
- 用户消息：右侧头像 😊 + amber-red 渐变气泡
- hover 显示时间 + 复制按钮

**输入框**：
- 圆角输入框内嵌发送按钮（箭头图标）
- 输入框有内容时显示发送按钮，无内容时隐藏
- Enter 键直接发送
- 发送按钮：amber→red 渐变，loading 时显示旋转动画

**流式交互**：
- 调用 `chatStream()` SSE 接口，逐 token 渲染
- 流式失败时 fallback 到非流式 `chat()` 接口
- 完成后自动刷新侧边栏会话列表

#### API 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/chat/stream` | SSE 流式对话 |
| POST | `/api/v1/chat` | 非流式对话（fallback） |
| GET | `/api/v1/chat/sessions` | 会话列表 |
| GET | `/api/v1/chat/session/{context_id}` | 会话详情 |
| DELETE | `/api/v1/chat/session/{context_id}` | 删除会话 |

---

### 3.3 AI 图片生成（核心功能）

#### 图片生成页 (`/image` - ImageGen.vue)

**界面布局**：
- 顶部：标题栏 "🎨 AI 图片生成"
- 中部：图片网格展示区（2-3列）
- 底部：输入框区域

**空状态**：
- 居中展示 "输入提示词，生成图片"
- 3 个快捷按钮：日落古镇 / 雪山湖泊 / 樱花小径

**图片卡片**：
- 网格布局展示已生成图片
- hover 显示下载 / 重新生成按钮
- 生成中显示骨架屏动画（流光 + 浮动粒子 + 画笔旋转 + 进度文字）

**输入框**：
- 圆角输入框，内嵌底部操作栏
- 底部栏左侧：风格下拉选择器 + 比例下拉选择器
- 底部栏右侧：发送按钮（图标，仅输入有内容时显示）
- Ctrl+Enter 发送

**风格选项**（8种）：
| 风格 | Prompt 描述 |
|------|-------------|
| 旅行海报 | 复古精致，有旅行杂志海报的质感 |
| 水墨画 | 中国传统水墨画风格，淡雅意境 |
| 油画 | 经典油画风格，笔触细腻，色彩浓郁 |
| 水彩画 | 水彩画风格 |
| 像素画 | 像素画风格 |
| 赛博朋克 | 赛博朋克风格，霓虹灯光，未来感 |
| 日系插画 | 日系动漫插画风格，色彩鲜明 |
| 写实摄影 | 写实摄影风格，高清逼真，光影自然 |

**比例选项**（11种）：
| 比例 | 图片尺寸 |
|------|----------|
| 1:1 | 2048×2048 |
| 2:3 | 1664×2496 |
| 3:2 | 2496×1664 |
| 3:4 | 1760×2368 |
| 4:3 | 2368×1760 |
| 4:5 | 1824×2272 |
| 5:4 | 2272×1824 |
| 9:16 | 1536×2752 |
| 16:9 | 2752×1536 |
| 9:21 | 1344×3136 |
| 21:9 | 3072×1376 |

**下拉框实现**：
- 自定义下拉选择器（非原生 select）
- 胶囊按钮触发器，点击展开面板
- 面板通过 `<Teleport to="body">` 挂载，`z-index: 9999`，不会被遮挡
- 面板固定宽度 200px，高度 80px，内容超出可滚动
- 选中项高亮，hover 半透明背景
- 展开/收起有 opacity + translateY 过渡动画
- 点击外部自动关闭

**流式交互**：
- 调用 `generateImageStream()` SSE 接口
- 进度事件：构思画面 → 生成图片 → 下载完成
- 图片 URL 事件：返回本地图片路径
- 完成事件：关闭 loading 状态

#### API 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/image/generate/stream` | SSE 流式图片生成 |

**请求参数**：
```json
{
  "prompt": "描述文本",
  "style": "旅行海报",
  "ratio": "1:1",
  "contextId": "可选"
}
```

**SSE 事件流**：
```
progress(step=1, "正在构思画面...")
progress(step=2, "正在生成图片...")
progress(step=3, "正在下载图片...")
image(imageUrl, contextId)
done("图片生成完成")
error(message)
```

---

### 3.4 旅游攻略生成

#### 攻略生成接口 (`/api/v1/travel`)

**请求参数**：
```json
{
  "destination": "杭州三日游",
  "days": 0,
  "preferences": ""
}
```
- `days=0` 时 AI 自动从 destination 文本解析天数和偏好

**SSE 事件流**：
```
progress(step=1, "正在规划行程...")
token(content) × N        → 流式攻略文本
text_done(full_content)   → 攻略文本完成
image_loading("正在生成目的地海报...")
image(url)                → 海报图片 URL
done("攻略生成完成")
```

**攻略文本结构**（AI System Prompt 要求）：
1. 行程概览
2. 每日详细行程（上午/下午/晚上）
3. 美食推荐
4. 住宿建议
5. 预算估算
6. 出行小贴士

---

### 3.5 侧边栏（App.vue）

**布局**：左侧 272px 固定侧边栏 + 右侧主内容区

**侧边栏内容**：
- Logo 区域：🤖 图标 + "AI 助手" 标题 + "智能对话·创意无限" 副标题
- 操作按钮：新对话 💬 / AI 生成图片 🎨（选中时 amber→red 渐变高亮）
- 会话历史列表：按时间排序，点击切换会话，显示会话类型图标
- 底部操作：主题切换（☀️/🌙/💻） / 退出登录 🚪

**会话管理**：
- 每次对话自动生成 contextId（`chat-xxx` 或 `image-xxx`）
- 侧边栏实时刷新会话列表
- 点击历史会话加载完整对话记录

---

### 3.6 历史记录页（History.vue）

> 注意：当前未注册到路由，不可通过 URL 访问

- 合并展示 report 和 chat 两种历史记录
- 按 contextId 分组，无 contextId 的按 5 分钟时间窗口分组
- 点击跳转 `/app?sessionId=xxx`
- 支持删除（确认弹窗）

---

### 3.7 设置页（Settings.vue）

> 注意：当前未注册到路由，不可通过 URL 访问

- 语言切换（zh-CN / en）
- 主题切换（浅色 / 深色 / 跟随系统）
- 字体大小、代码字体、消息密度设置
- 设置持久化到 localStorage

---

## 四、UI 设计规范

### 设计语言
- **主色调**：amber (暖橙) → red (渐变终点)
- **渐变**：`from-amber-500 to-red-500`（按钮、头像、高亮）
- **背景**：`from-amber-50 via-orange-50 to-yellow-50`（页面渐变）
- **卡片**：白色 + `border-2 border-amber-300` + `rounded-2xl`
- **暗色模式**：stone 灰色系列（stone-800/700/600）

### 交互规范
- 按钮 hover：`-translate-y-0.5` + `shadow-md`（微上浮）
- 输入框 focus：`ring-2 ring-amber-400` + `border-transparent`
- 消息 hover：显示时间 + 复制按钮（`opacity-0 → opacity-100`）
- 下拉框：Teleport 到 body，`z-index: 9999`，滑入滑出动画

### 组件风格
| 元素 | 样式 |
|------|------|
| 按钮（主要） | `bg-gradient-to-r from-amber-500 to-red-500 rounded-xl shadow-md` |
| 按钮（次要） | `bg-white border-2 border-amber-300 rounded-full` |
| 输入框 | `bg-amber-50 border-2 border-amber-200 rounded-xl` |
| 卡片 | `bg-white border-2 border-amber-300 rounded-2xl shadow-sm` |
| AI 头像 | `bg-gradient-to-br from-amber-500 to-red-500 rounded-full` |
| 用户头像 | `bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full` |

---

## 五、数据库模型

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名（唯一） |
| email | String(100) | 邮箱（唯一） |
| hashed_password | String(255) | 加密密码 |
| full_name | String(100) | 全名（可选） |
| is_active | Boolean | 是否激活 |
| is_superuser | Boolean | 是否超管 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### chat_histories 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户 ID（FK） |
| context_id | String(64) | 会话分组 ID |
| image_url | String(500) | 图片 URL |
| title | String(100) | 会话标题 |
| user_message | Text | 用户消息 |
| ai_reply | Text | AI 回复 |
| created_at | DateTime | 创建时间 |

### report_histories 表（遗留）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户 ID（FK） |
| file_id | String | 文件 ID |
| file_name | String | 文件名 |
| user_prompt | Text | 用户提示词 |
| generated_prompt | Text | 生成的提示词 |
| image_url | String | 图片 URL |
| dashboard_spec | Text | 仪表盘规格 JSON |
| status | String | 状态 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

## 六、重试与容错机制

所有 AI 服务调用（聊天、攻略生成、图片生成）均采用统一重试策略：
- **最大重试次数**：3 次
- **重试间隔**：1s → 2s → 4s（递增）
- **可重试条件**：429 限流、5xx 服务端错误、网络超时/连接错误
- **不可重试**：已输出部分内容后出错（避免内容重复）、4xx 客户端错误

---

## 七、遗留模块（待清理）

以下模块属于原始"报表生成平台"功能，当前仍存在于代码中但非核心需求：

| 模块 | 文件 | 说明 |
|------|------|------|
| Excel 上传 | `upload.py` | 上传 Excel 文件，解析数据 |
| 报表生成 | `generate.py` | 两阶段报表生成（规格 → 确认） |
| 任务管理 | `task.py` | 内存任务状态查询（无持久化） |
| SSE 推送 | `sse.py` | 任务进度 SSE 推送 |
| 报表历史 | `history.py` | 报表历史 CRUD |
| LandingPage | `LandingPage.vue` | 营销落地页（未注册路由） |
| Help | `Help.vue` | 帮助页（未注册路由） |
| ECharts | `vue-echarts` | 图表渲染组件（未使用） |

---

## 八、路由配置

| 路径 | 页面 | 认证 |
|------|------|------|
| `/` | 重定向到 `/app` | — |
| `/app` | Home.vue（对话页） | 必需 |
| `/app?sessionId=xxx` | Home.vue（加载历史会话） | 必需 |
| `/image` | ImageGen.vue（图片生成页） | 必需 |
| `/login` | Login.vue | 仅游客 |
| `/register` | Register.vue | 仅游客 |
| `/*` | NotFound.vue | — |

---

## 九、前端 Store 结构

| Store | 文件 | 职责 |
|-------|------|------|
| auth | `auth.ts` | 用户认证状态、token、login/register/logout/checkAuth |
| session | `session.ts` | 会话列表加载与实时更新 |
| app | `app.ts` | 全局设置（语言、主题、字体）、消息状态、侧边栏 |

---

## 十、项目目录结构

```
st-agent/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由（auth, chat, travel, image, 遗留模块）
│   │   ├── models/       # 数据模型（user, chat_history, report_history）
│   │   ├── services/     # 业务服务（ai_service, chat_history, user, task, history）
│   │   ├── utils/        # 工具（security, common, file_utils）
│   │   ├── config.py     # 配置（数据库、AI、JWT、CORS）
│   │   └── main.py       # FastAPI 入口
│   ├── generated/        # AI 生成的图片存储目录
│   ├── uploads/          # 上传文件目录
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/        # 页面组件（Home, ImageGen, Login, Register, History, Settings, etc.）
│   │   ├── components/   # 通用组件（MarkdownRenderer, Toast）
│   │   ├── stores/       # Pinia Store（auth, session, app）
│   │   ├── services/     # API 服务（api.ts, auth.ts）
│   │   ├── i18n/         # 国际化（zh-CN, en）
│   │   ├── types/        # TypeScript 类型定义
│   │   ├── composables/  # 组合式函数（useToast）
│   │   ├── router/       # Vue Router 配置
│   │   ├── style.css     # 全局样式 + 设计系统变量
│   │   └── App.vue       # 应用外壳（侧边栏 + 主内容区）
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── xuqiu.md              # 本需求文档
└── .gitignore
```