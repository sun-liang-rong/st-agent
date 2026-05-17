# AI 报表生成平台 - 后端

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 主应用
│   ├── config.py            # 配置文件
│   ├── models/              # 数据模型
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑服务
│   └── utils/               # 工具函数
├── uploads/                 # 上传文件存储
├── generated/               # 生成的文件
├── .env.example
├── requirements.txt
└── README.md
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者使用 Docker
docker-compose up
```

## API 文档

启动服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
