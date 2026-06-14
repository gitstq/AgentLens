<div align="center">

# 🔍 AgentLens

**AI 代理會話智能分析平台**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](https://github.com/gitstq/AgentLens/releases)

<p align="center">
  <img src="docs/logo.svg" alt="AgentLens Logo" width="120">
</p>

**追蹤、分析並最佳化您的 AI 代理會話**

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

</div>

---

## 🎉 專案介紹

AgentLens 是一款專為 AI 編碼代理和對話式 AI 工具設計的綜合分析平台。它幫助開發者追蹤、分析並最佳化 AI 代理會話，提供詳細的 Token 使用量、成本和效能指標洞察。

無論您使用 Claude Code、Cursor、GitHub Copilot 還是其他任何 AI 代理，AgentLens 都能為您提供所需的能見度，幫助您理解並改進 AI 輔助開發工作流程。

## ✨ 核心特性

- 📊 **即時儀表板** - 精美的 Web 介面，即時會話統計
- 💰 **成本追蹤** - 自動 Token 計數和成本估算
- 🤖 **多代理支援** - 支援 Claude、Cursor、Codex 等
- 📈 **分析與報表** - 每日趨勢、代理對比、成本分析
- 🖥️ **CLI 工具** - 命令列介面，快速管理會話
- 🔒 **本地優先** - 資料本地儲存，隱私有保障
- 🌐 **REST API** - 功能完整的 API，支援自定義整合
- 📱 **響應式介面** - 支援桌面、平板和行動裝置

## 🚀 快速開始

### 環境要求

- Python 3.10+
- Node.js 18+（前端開發）

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/AgentLens.git
cd AgentLens

# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝前端依賴（可選，用於開發）
cd frontend
npm install
```

### 啟動服務

```bash
# 啟動 API 服務
python -m src.main

# 或使用 CLI
python -m src.cli.main serve
```

Web 儀表板將可在 `http://localhost:8000` 訪問

### 使用 CLI

```bash
# 開始新會話
python -m src.cli.main start --agent claude --project my-project

# 記錄命令
python -m src.cli.main log <session-id> "git commit -m 'update'"

# 結束會話並統計
python -m src.cli.main end <session-id> --input-tokens 1000 --output-tokens 500

# 查看分析
python -m src.cli.main stats
```

## 📖 詳細使用指南

### 會話追蹤

1. **開始會話**: 開始使用 AI 代理時啟動追蹤
2. **記錄命令**: 記錄每次互動以進行詳細分析
3. **結束會話**: 使用 Token 數量完成，用於成本計算

### Web 儀表板

- **儀表板**: 所有會話、成本和趨勢概覽
- **會話列表**: 詳細列表，支援篩選和搜尋
- **分析報表**: 圖表和報告，深入洞察
- **設定**: 配置定價和偏好

### API 介面

| 介面 | 方法 | 說明 |
|------|------|------|
| `/api/v1/sessions` | GET | 列出所有會話 |
| `/api/v1/sessions` | POST | 建立新會話 |
| `/api/v1/sessions/{id}` | GET | 取得會話詳情 |
| `/api/v1/sessions/{id}` | PATCH | 更新會話 |
| `/api/v1/commands` | POST | 記錄命令 |
| `/api/v1/analytics/summary` | GET | 取得分析摘要 |

## 💡 設計思路與迭代規劃

### 設計原則

- **隱私優先**: 所有資料保存在本地
- **開發者友善**: 簡潔的 CLI，強大的 API
- **可擴展**: 輕鬆添加新代理類型和指標
- **輕量級**: 資源占用最小化

### 路線圖

- [ ] 匯出 PDF/CSV 報告
- [ ] 團隊協作功能
- [ ] 與主流 IDE 整合
- [ ] 高級成本最佳化建議
- [ ] 多語言支援擴展

## 📦 打包與部署

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

### 構建前端

```bash
cd frontend
npm run build
```

### 執行測試

```bash
pytest tests/ -v
```

## 🤝 貢獻指南

我們歡迎貢獻！請參閱 [貢獻指南](CONTRIBUTING.md) 了解詳情。

1. Fork 本倉庫
2. 建立您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某個特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 開源協議

本專案基於 MIT 協議開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**為 AI 開發者社群精心打造 ❤️**

[報告 Bug](https://github.com/gitstq/AgentLens/issues) · [請求特性](https://github.com/gitstq/AgentLens/issues)

</div>
