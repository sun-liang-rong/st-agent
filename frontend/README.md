# AI 旅游攻略与图片生成平台 - 前端

Vue 3 + TypeScript + Vite 前端应用，提供登录注册、旅游攻略对话、图片生成和历史会话管理界面。

## 快速开始

```bash
npm install
npm run dev
```

默认开发地址为 http://localhost:5173。

## 可用脚本

```bash
npm run dev      # 启动开发服务
npm run build    # 类型检查并构建生产包
npm run preview  # 预览生产包
```

## 代理配置

开发环境 Vite 代理位于 `vite.config.ts`：

- `/api` -> `http://localhost:8000/api/v1`
- `/generated` -> `http://localhost:8000/generated`

请先启动后端服务，再使用对话、图片生成和历史记录功能。
