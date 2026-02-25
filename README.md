# 🧠 OpenCode Smart Model Selector V1.0

**智能模型调度系统 V1.0 - 任何 API 都能智能切换**

---

## 🎯 核心定位

> **智能无感知选择最优模型，默认不需要用户任何操作**

用户在 OpenCode 窗口说话 → 系统自动分析任务 → 自动选择最优模型 → 自动执行 → 返回结果

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **🤖 智能无感知（默认）** | 用户说话，系统自动选最优模型，全程不需要用户选择 |
| **🔄 多 Key 轮换** | 任何 API 都能配置，多 Key 负载均衡 |
| **🛡️ 故障自动转移** | 主 API 不可用？自动切换备用，无需手动 |
| **💰 成本优化** | 付费/免费 API 智能调度 |
| **🏭 任意 Provider** | 只要能对接的 API 都可以 |

---

## 🤖 智能模式（默认）

用户在 OpenCode 窗口说话，系统自动完成一切：

```
用户输入: "帮我写一个项目"

↓ 系统自动 ↓

1. 分析任务 → "这是一个开发任务"
2. 选择模型 → 选 Claude（适合开发）
3. 执行任务 → 返回结果

用户只需要说话，其他都是系统自动完成！
```

---

## 🎮 手动模式（可选）

如果用户想手动指定模型，可以使用：

```bash
./op.sh -m    # 研究模式
./op.sh -c    # 编程模式
./op.sh -f    # 极速模式
./op.sh -cn   # 中文模式
```

---

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

---

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
# 想配什么配什么
```

或创建 `~/.local/share/opencode/auth.json`：

```json
{
  "google_api_key": "xxx",
  "deepseek_api_key": "xxx"
}
```

### 3. 运行

```bash
# 智能无感知模式（默认）
./op.sh "你的任务"

# 手动模式（可选）
./op.sh -m "任务"    # 研究模式
./op.sh -c "任务"    # 编程模式
./op.sh -f "任务"    # 极速模式
```

---

## 📖 两种使用方式

### 方式一：智能无感知（推荐）

用户在 OpenCode 窗口直接说话：

```
"帮我写一个Python脚本"
"分析这段代码"
"翻译这段英文"
```

**系统自动分析任务类型，选择最适合的模型，用户不需要做任何选择！**

### 方式二：手动指定（可选）

如果用户想指定用某个模型：

```bash
./op.sh google/gemini-3.1-pro "任务"      # 指定 Google
./op.sh deepseek/deepseek-chat "任务"     # 指定 DeepSeek
./op.sh anthropic/claude-sonnet "任务"    # 指定 Claude

./op.sh -m "任务"    # 研究模式
./op.sh -c "任务"    # 编程模式
./op.sh -f "任务"    # 极速模式
```

---

## 🏗️ 系统架构

```
用户输入（在 OpenCode 窗口）
    │
    ▼
┌─────────────────────┐
│   智能分析引擎       │
│  • 分析任务类型     │
│  • 分析任务复杂度   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   自动选最优模型    │
│  • 编程 → Claude  │
│  • 中文 → Kimi    │
│  • 简单 → 免费模型 │
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
│           └── ...   │
└─────────────────────┘
```

---

## 📁 项目结构

```
smart-model-selector/
├── smart_model_dispatcher.py  # 核心调度引擎
├── model_selector.py          # 智能模型选择
├── daemon.py                 # 守护进程
├── op.sh                     # 启动脚本
└── README.md                 # 本文档
```

---

## 🔧 支持的 Provider

| Provider | 环境变量 | 说明 |
|----------|----------|------|
| Google Gemini | `GOOGLE_API_KEYS` | 主力首选 |
| Claude | `ANTHROPIC_API_KEY` | 代码/分析强 |
| DeepSeek | `DEEPSEEK_API_KEY` | 性价比高 |
| OpenRouter | `OPENROUTER_API_KEY` | 万能备选 |
| Kimi | `KIMI_API_KEY` | 中文优化 |
| 豆包 | `DOUBAO_API_KEY` | 中文优化 |
| 硅基流动 | `SILICONFLOW_API_KEY` | 多模型 |
| MiniMax | `MINIMAX_API_KEY` | 中文优化 |
| Groq | `GROQ_API_KEY` | 极速 |
| 智谱 | `ZHIPUAI_API_KEY` | 中文免费 |

---

## ⚠️ 注意事项

1. **智能无感知是默认**：用户只需要说话，系统自动选模型
2. **手动是可选的**：只有特殊需求才用 `./op.sh -m` 等
3. **安全存储**：API Key 存 `~/.local/share/openopenauth.json`
4. **不修改 opencode.json**：不会影响 OpenCode 官方配置

---

## 📜 许可证

MIT

---

**智能无感知选择最优模型，默认不需要用户任何操作！**

⭐️ Star: https://github.com/wuleiyuan/opencode-smart-model-selector
