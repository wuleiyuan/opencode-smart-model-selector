# 🧠 OpenCode Smart Model Selector

[![Version](https://img.shields.io/badge/Version-v2.0.0-blue.svg)](https://github.com/wuleiyuan/opencode-smart-model-selector/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/wuleiyuan/opencode-smart-model-selector?style=social)](https://github.com/wuleiyuan/opencode-smart-model-selector/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/wuleiyuan/opencode-smart-model-selector/main.svg)](https://github.com/wuleiyuan/opencode-smart-model-selector/commits/main)

> 🇨🇳 中文 | [English](./README_EN.md)

**OpenCode 智能模型调度系统** - 基于任务类型自动选择最优 AI 模型，支持多 Provider 负载均衡、故障自动转移、成本优化。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **智能路由** | 根据任务类型自动选择最优模型 (Coding/Research/Fast) |
| ⚡ **负载均衡** | 多 API Key 轮询，避免单点限流 |
| 🛡️ **故障转移** | API 故障自动切换，用户无感知 |
| 💰 **成本优化** | 长文本自动降级，免费模型优先 |
| ⏰ **智能 TTL** | 手动指定模型 24h 过期，自动恢复智能模式 |
| 🔄 **热启动** | 测速记忆持久化，重启后无需重新探测网络 |
| 🖥️ **多 Shell 支持** | 支持 Zsh 和 Bash 自动启动 |

## 🚀 快速开始

### 安装

```bash
cd /path/to/smart-model-selector
pip install -r requirements.txt
```

### 配置 API Key

在 `auth.json` 中配置你的 API Key：

```json
{
  "google_api_key": "your-google-api-key",
  "anthropic_api_key": "your-anthropic-key",
  "deepseek_api_key": "your-deepseek-key"
}
```

### 基本使用

```bash
# 🎯 全自动模式 (推荐) - 直接输入任务描述
op 帮我写一个 Python 排序算法
op 分析这段代码的性能问题
op 翻译这段英文到中文

# 📋 手动模式 - 显式指定
op -m              # 研究模式 (Google Gemini Pro)
op -c              # 编程模式 (Claude 3.5/3.7)
op -f              # 极速模式 (免费模型优先)
op -w              # 吞吐模式 (DeepSeek/豆包)
op -cn             # 中文模式 (硅基流动/MiniMax)

# 🔧 高级功能
op set google/gemini-2.0-pro  # 指定模型 (24h 有效)
op auto                       # 恢复到智能模式
op version                    # 查看版本信息
op current                   # 显示当前配置
```

## 📊 支持的模型

| Provider | 模型 | 特点 |
|----------|------|------|
| Google Gemini | 2.0 Pro / 1.5 Pro | 高性能、长上下文 |
| Anthropic Claude | 3.5/3.7 Sonnet | 编程王者、推理专家 |
| DeepSeek | Chat / Coder | 性价比高、中文优化 |
| SiliconFlow | Qwen/DeepSeek 免费 | 免费额度多 |
| MiniMax | Chat | 中文场景优化 |

## 🏗️ 项目架构

```
smart-model-selector/
├── smart_model_dispatcher.py  # 核心调度引擎
├── model_selector.py           # 任务分析模型选择
├── daemon.py                   # 后台守护进程
├── version.py                  # 版本管理
├── op.sh                      # 命令行工具
├── auto_start.sh              # 自动启动脚本
├── api_config.json            # API 配置模板
└── README.md                  # 项目文档
```

## 📈 功能详解

### 智能模型选择

系统会根据任务描述自动分析并选择最优模型：

```python
# 任务分析 -> 模型匹配
"写代码" -> Coding 模式 -> Claude
"分析数据" -> Research 模式 -> Gemini Pro
"翻译" -> Fast 模式 -> 免费模型
```

### 故障处理机制

```
Primary API 故障 → 自动切换 Secondary API
全部故障 → 切换 Emergency Pool (OpenRouter)
限流 429 → 进入冷静期 (10分钟)
```

### 成本优化策略

- 长文本 (>8000 tokens) 自动降级到免费模型
- 免费模型优先使用
- 任务复杂度评估选择合适模型

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

## 📄 License

MIT License - 查看 [LICENSE](LICENSE) 了解详情

---

**⭐ 如果这个项目对你有帮助，请点个 Star 支持一下！**
