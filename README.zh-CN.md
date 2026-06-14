<div align="center">

# 🔍 AgentLens

**AI 代理会话智能分析平台**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](https://github.com/gitstq/AgentLens/releases)

<p align="center">
  <img src="docs/logo.svg" alt="AgentLens Logo" width="120">
</p>

**追踪、分析并优化您的 AI 代理会话**

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

</div>

---

## 🎉 项目介绍

AgentLens 是一款专为 AI 编码代理和对话式 AI 工具设计的综合分析平台。它帮助开发者追踪、分析并优化 AI 代理会话，提供详细的 Token 使用量、成本和性能指标洞察。

无论您使用 Claude Code、Cursor、GitHub Copilot 还是其他任何 AI 代理，AgentLens 都能为您提供所需的可见性，帮助您理解并改进 AI 辅助开发工作流。

## ✨ 核心特性

- 📊 **实时仪表盘** - 精美的 Web 界面，实时会话统计
- 💰 **成本追踪** - 自动 Token 计数和成本估算
- 🤖 **多代理支持** - 支持 Claude、Cursor、Codex 等
- 📈 **分析与报表** - 每日趋势、代理对比、成本分析
- 🖥️ **CLI 工具** - 命令行界面，快速管理会话
- 🔒 **本地优先** - 数据本地存储，隐私有保障
- 🌐 **REST API** - 功能完整的 API，支持自定义集成
- 📱 **响应式界面** - 支持桌面、平板和移动设备

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+（前端开发）

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/AgentLens.git
cd AgentLens

# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖（可选，用于开发）
cd frontend
npm install
```

### 启动服务

```bash
# 启动 API 服务
python -m src.main

# 或使用 CLI
python -m src.cli.main serve
```

Web 仪表盘将可在 `http://localhost:8000` 访问

### 使用 CLI

```bash
# 开始新会话
python -m src.cli.main start --agent claude --project my-project

# 记录命令
python -m src.cli.main log <session-id> "git commit -m 'update'"

# 结束会话并统计
python -m src.cli.main end <session-id> --input-tokens 1000 --output-tokens 500

# 查看分析
python -m src.cli.main stats
```

## 📖 详细使用指南

### 会话追踪

1. **开始会话**: 开始使用 AI 代理时启动追踪
2. **记录命令**: 记录每次交互以进行详细分析
3. **结束会话**: 使用 Token 数量完成，用于成本计算

### Web 仪表盘

- **仪表盘**: 所有会话、成本和趋势概览
- **会话列表**: 详细列表，支持筛选和搜索
- **分析报表**: 图表和报告，深入洞察
- **设置**: 配置定价和偏好

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/sessions` | GET | 列出所有会话 |
| `/api/v1/sessions` | POST | 创建新会话 |
| `/api/v1/sessions/{id}` | GET | 获取会话详情 |
| `/api/v1/sessions/{id}` | PATCH | 更新会话 |
| `/api/v1/commands` | POST | 记录命令 |
| `/api/v1/analytics/summary` | GET | 获取分析摘要 |

## 💡 设计思路与迭代规划

### 设计原则

- **隐私优先**: 所有数据保存在本地
- **开发者友好**: 简洁的 CLI，强大的 API
- **可扩展**: 轻松添加新代理类型和指标
- **轻量级**: 资源占用最小化

### 路线图

- [ ] 导出 PDF/CSV 报告
- [ ] 团队协作功能
- [ ] 与主流 IDE 集成
- [ ] 高级成本优化建议
- [ ] 多语言支持扩展

## 📦 打包与部署

### Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

### 构建前端

```bash
cd frontend
npm run build
```

### 运行测试

```bash
pytest tests/ -v
```

## 🤝 贡献指南

我们欢迎贡献！请参阅 [贡献指南](CONTRIBUTING.md) 了解详情。

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某个特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 开源协议

本项目基于 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">

**为 AI 开发者社区精心打造 ❤️**

[报告 Bug](https://github.com/gitstq/AgentLens/issues) · [请求特性](https://github.com/gitstq/AgentLens/issues)

</div>
