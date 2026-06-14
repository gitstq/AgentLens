<p align="center">
  <img src="../assets/logo.jpg" alt="AgentLens Logo" width="120" height="120" />
</p>

<h1 align="center">AgentLens</h1>

<p align="center">
  <strong>輕量級AI編碼代理會話智能分析引擎</strong><br/>
  Lightweight AI Coding Agent Session Intelligence Analysis Engine
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Platform-Cross--Platform-informational.svg" alt="Cross Platform" />
  <img src="https://img.shields.io/badge/Tests-28%20Passed-brightgreen.svg" alt="Tests" />
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version" />
</p>

---

## 專案介紹

AgentLens 是一款輕量級、零依賴的 CLI 工具，能智能分析您的 AI 編碼代理會話。它自動偵測來自 Claude Code、Cursor、Trae、Windsurf、Copilot、Aider 等代理的會話資料，提供關於使用模式、Token 消耗、成本及最佳化建議的深度洞察。

**為什麼需要 AgentLens？** 隨著 AI 編碼代理成為開發者的必備工具，了解您如何使用它們——以及它們花費多少——至關重要。AgentLens 為您的 AI 編碼工作流程提供清晰、可操作的視圖。

## 核心特性

- **多代理支援** — 自動偵測並解析 10+ 種 AI 編碼代理的會話
- **成本智能** — 追蹤跨模型的 Token 使用量和成本，提供智慧預測
- **使用分析** — 每日/每週模式、尖峰時段、會話長度分佈
- **終端儀表板** — 美觀的彩色 TUI 儀表板，含進度條
- **多格式匯出** — JSON、CSV、Markdown、SARIF，支援 CI/CD 整合
- **最佳化建議** — AI 驅動的建議，幫助降低成本、提高效率
- **零依賴** — 純 Python 3.8+，單檔安裝，跨平台
- **隱私優先** — 100% 本地分析，資料不離開您的機器

## 快速開始

### 安裝

```bash
# 從 PyPI 安裝（推薦）
pip install agentlens

# 或從原始碼安裝
git clone https://github.com/gitstq/AgentLens.git
cd AgentLens
pip install -e .
```

### 使用方式

```bash
# 偵測已安裝的 AI 編碼代理
agentlens agents

# 顯示分析儀表板
agentlens dashboard

# 掃描並分析會話
agentlens scan

# 顯示成本分析與預測
agentlens cost

# 列出最近的會話
agentlens sessions --limit 10

# 匯出為 Markdown 報告
agentlens export --format markdown --output report.md

# 匯出為 CSV
agentlens export --format csv --output analysis.csv

# 掃描特定代理
agentlens scan --agent claude-code

# 掃描自訂目錄
agentlens scan --path /path/to/sessions
```

## 支援的代理

| 代理 | 狀態 | 解析器 |
|------|--------|--------|
| Claude Code | 完整支援 | JSON/JSONL |
| Cursor | 完整支援 | JSON |
| Trae | 完整支援 | JSON/JSONL |
| Windsurf | 完整支援 | JSON |
| GitHub Copilot | 基礎支援 | JSON |
| Aider | 基礎支援 | JSONL |
| Continue | 基礎支援 | JSON |
| 通義靈碼 | 基礎支援 | JSON |
| Codeium | 基礎支援 | JSON |
| 通用 | 後備方案 | JSON/JSONL/Text |

## 設計與架構

```
AgentLens/
├── src/agentlens/
│   ├── models/       # 資料模型（Session、Message、CostRecord）
│   ├── parsers/      # 代理特定的會話解析器
│   ├── analyzers/    # 會話、成本和使用分析器
│   ├── exporters/    # 多格式匯出（JSON/CSV/MD/SARIF）
│   ├── ui/           # 終端 UI（顏色、表格、儀表板）
│   ├── utils/        # 工具函數（成本估算、路徑偵測）
│   └── cli.py        # CLI 進入點
├── tests/            # 單元測試（28 個測試，100% 通過）
├── assets/           # 專案標誌
└── pyproject.toml    # 建構配置
```

## 迭代規劃

- [ ] Web UI 儀表板
- [ ] 歷史趨勢圖表
- [ ] 會話比較與差異
- [ ] 外掛系統
- [ ] 即時會話監控
- [ ] 團隊/共享分析
- [ ] VS Code 擴充功能

## 貢獻指南

歡迎貢獻！請依照以下步驟：

1. Fork 此儲存庫
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 提交您的變更（`git commit -m 'feat: add amazing feature'`）
4. 推送至分支（`git push origin feature/amazing-feature`）
5. 開啟 Pull Request

## 開源協議

本專案採用 MIT 協議 — 詳見 [LICENSE](../LICENSE) 檔案。

---

<p align="center">
  使用 Python 建構，由 <a href="https://github.com/gitstq">AgentLens Team</a> 維護
</p>
