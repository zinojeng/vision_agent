# Vision Agent

這是一個基於 LandingAI API 的智能文件分析工具，結合了 Anthropic Claude-3.5 和 OpenAI API 來提供最佳性能。目前支持以下功能：

## 功能特點

- PDF 文件解析與分析
- 智能文本提取
- 文件結構識別
- 多 LLM 支持（Anthropic Claude-3.5 和 OpenAI）

## 安裝要求

- Python 3.8+
- 相關依賴套件（見 requirements.txt）

## 快速開始

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 設置環境變數：
```bash
export LANDING_AI_API_KEY=your_landing_ai_key
export ANTHROPIC_API_KEY=your_anthropic_key
export OPENAI_API_KEY=your_openai_key
```

3. 使用範例：
```python
from vision_agent.tools.pdf_parser import PDFParser
from vision_agent.utils.config import Config

config = Config()
parser = PDFParser(config)
result = parser.process_pdf("path/to/your/document.pdf")
```

## 專案結構

```
vision_agent/
├── tools/
│   └── pdf_parser.py     # PDF 解析工具
├── utils/
│   ├── config.py         # 配置管理
│   └── logger.py         # 日誌工具
└── examples/             # 使用範例
```

## LLM 提供者配置

本專案默認使用 Anthropic Claude-3.5 和 OpenAI API 的組合來提供最佳性能。你需要：

1. 在 [Anthropic](https://www.anthropic.com/) 註冊並獲取 API 金鑰
2. 在 [OpenAI](https://openai.com/) 註冊並獲取 API 金鑰
3. 在 [LandingAI](https://landing.ai/) 註冊並獲取 API 金鑰

所有 API 金鑰都應該通過環境變數設置。

## 授權

MIT License

## 貢獻指南

歡迎提交 Pull Requests 來改善這個專案。
