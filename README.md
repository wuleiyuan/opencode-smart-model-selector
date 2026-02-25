# 🧠 OpenCode Smart Model Selector V1.0

**智能模型调度系统 V1.0 - 任何 API 都能智能切换**

---

## 🎯 核心定位

> **主打智能切换模型。任何 API 都可以。**

无论你有什么 API——Google、Claude、DeepSeek、OpenRouter、Kimi、硅基流动……甚至更多——只要配置好，系统自动为你智能调度！

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **🤖 智能切换** | 根据任务自动选择最优模型 |
| **🔄 万物可轮换** | 任何 API 都能配置，多 Key 轮换负载均衡 |
| **🛡️ 故障自动转移** | 主 API 不可用？自动切换备用，无需手动 |
| **💰 成本优化** | 付费/免费 API 智能调度 |
| **🏭 任意 Provider** | 只要能对接的 API 都可以 |

## 🤔 这系统能做什么？

```
你配置: Google API + DeepSeek API + OpenRouter API + 任何其他 API

系统自动:
├── Google 可用 → 用 Google
├── Google 限额 → 自动切换 DeepSeek
├── DeepSeek 不可用 → 自动切换 OpenRouter
├── OpenRouter 也不行 → 继续切换下一个配置的 API
└── 全都挂了 → 报错（但不会卡死）
```

### 简单说：只要你有 API，系统就能帮你轮换着用！

## 🚀 快速开始

### 1. 克隆

```bash
git clone https://github.com/wuleiyuan/opencode-smart-model-selector.git
cd opencode-smart-model-selector
```

### 2. 配置 API（任何 API 都可以！）

```bash
# 环境变量方式（推荐）
export GOOGLE_API_KEYS="你的google key"
export DEEPSEEK_API_KEYS="你的deepseek key"
export OPENROUTER_API_KEYS="你的openrouter key"
# 想配什么配什么，系统会自动识别
```

或创建 `~/.local/share/opencode/auth.json`：

```json
{
  "google_api_key": "xxx",
  "deepseek_api_key": "xxx",
  "openai_api_key": "xxx",
  "any_other_api_key": "xxx"
}
```

### 3. 运行

```bash
./op.sh "你的任务"
```

## 📖 典型场景

### 场景1: 只有一个 API

```bash
export GOOGLE_API_KEYS="only-one-key"
./op.sh "写个函数"
```
✅ 正常工作

### 场景2: 有多个同类型 API

```bash
export GOOGLE_API_KEYS="key1 key2 key3"
./op.sh "写个函数"
```
✅ 3个 Key 轮换用，负载均衡

### 场景3: 多种 API 混合

```bash
export GOOGLE_API_KEYS="google-key"
export DEEPSEEK_API_KEYS="deepseek-key"  
export OPENROUTER_API_KEYS="openrouter-key"
export ANTHROPIC_API_KEYS="claude-key"
# 想加多少加多少
```
✅ 按顺序自动切换：Google → DeepSeek → OpenRouter → Claude

### 场景4: 付费 + 免费

```bash
export GOOGLE_API_KEYS="paid-key"
export GOOGLE_FREE_API_KEYS="free-key"
export OPENROUTER_API_KEYS="free-key"
```
✅ 付费优先 → 限额自动切免费

## 🎮 使用方式

### 手动选择模型

```bash
./op.sh google/gemini-3.1-pro "任务"      # 指定用 Google
./op.sh deepseek/deepseek-chat "任务"     # 指定用 DeepSeek
./op.sh anthropic/claude-sonnet "任务"    # 指定用 Claude
./op.sh openrouter/auto "任务"            # 指定用 OpenRouter
```

### 自动智能选择

```bash
./op.sh "任务描述"
```
系统自动分析任务类型，选择最优模型：
- 编程任务 → 优先 Claude
- 中文任务 → 优先 Kimi/豆包
- 简单任务 → 优先免费模型
- 复杂任务 → 优先付费 Pro 模型

### 后台无感知切换

配置多个 API 后，系统在后台自动处理：
- 负载均衡（多个 Key 轮换）
- 故障转移（一个挂了用另一个）
- 额度控制（免费额度用完自动切付费）

## 🏗️ 系统架构

```
用户请求
    │
    ▼
┌─────────────────────┐
│   智能模型选择器     │
│  • 分析任务类型     │
│  • 分析任务复杂度   │
│  • 选择最优模型    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    API 调度引擎    │
│                     │
│  API1 → 成功 → 返回│
│    │               │
│    └── 失败 → API2 │
│           │         │
│           └── 失败 → API3 │
│                   │     │
│                   └── ...│
└─────────────────────┘
```

## 📁 项目结构

```
smart-model-selector/
├── smart_model_dispatcher.py  # 核心调度引擎
├── model_selector.py          # 智能模型选择
├── daemon.py                 # 守护进程
├── op.sh                    # 启动脚本
└── README.md               # 本文档
```

## 🔧 支持的 Provider（任何 API 都可以）

| Provider | 环境变量 | 说明 |
|----------|----------|------|
| Google Gemini | `GOOGLE_API_KEYS` | 主力首选 |
| Claude | `ANTHROPIC_API_KEY` | 代码/分析强 |
| DeepSeek | `DEEPSEEK_API_KEY` | 性价比高 |
| OpenRouter | `OPENROUTER_API_KEY` | 万能备选 |
| Kimi (Moonshot) | `KIMI_API_KEY` | 中文优化 |
| 豆包 (Doubao) | `DOUBAO_API_KEY` | 中文优化 |
| 硅基流动 | `SILICONFLOW_API_KEY` | 多模型 |
| MiniMax | `MINIMAX_API_KEY` | 中文优化 |
| 阿里云 (Qwen) | `DOUBAO_API_KEY` | 中文优化 |
| Groq | `GROQ_API_KEY` | 极速 |
| OpenAI | `OPENAI_API_KEY` | 通用 |
| 智谱 (Zhipu) | `ZHIPUAI_API_KEY` | 中文免费 |
| ModelScope | `MODELSCOPE_API_KEY` | 开源模型 |

### 任何其他 API？

只要提供 `xxx_api_key` 环境变量，系统会自动识别并接入！

## ⚠️ 注意事项

1. **需要自备 API**: 系统不提供任何 API Key，需要用户自己配置
2. **安全存储**: API Key 存 `~/.local/share/openopenauth.json`，不写入配置文件
3. **不修改 opencode.json**: 不会影响 OpenCode 官方配置

## 📜 许可证

MIT

---

**主打智能切换模型。任何 API 都可以。**

⭐️ Star: https://github.com/wuleiyuan/opencode-smart-model-selector
