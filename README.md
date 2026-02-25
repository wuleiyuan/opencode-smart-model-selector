# 🧠 OpenCode 智能模型调度系统 v2.0.0

## ✨ 核心特性

- **5个Gemini 3 Pro轮询**: 智能负载均衡，避免单点限流
- **多Provider支持**: Google、Anthropic、DeepSeek、SiliconFlow、MiniMax等
- **静默自愈**: API故障自动切换，用户无感知
- **冷静期管理**: 429限流智能冷却
- **紧急熔断**: OpenRouter终极备选，永不宕机
- **一键切换**: 简单命令激活不同模式

## 🚀 快速开始

### 安装依赖
```bash
cd /path/to/smart-model-selector
pip install -r requirements.txt
```

### 基本使用

```bash
# 激活研究模式 (Gemini 3 Pro轮询)
op -m

# 激活编程模式 (Claude 3.5优先)
op -c

# 激活极速模式 (备用模型优先)
op -f

# 查看当前状态
op current

# 智能任务选择
op smart "分析股票数据"  # 自动选择编程模式
```

## 📁 项目结构

```
smart-model-selector/
├── smart_model_dispatcher.py  # 核心调度引擎
├── api_config.json         # API密钥配置
├── op.sh                  # 命令行接口
├── requirements.txt          # Python依赖
└── README.md             # 项目文档
```

## 🔧 配置文件说明

### api_config.json 结构
```json
{
  "api_keys": {
    "gemini_pro_paid": [...],      # 5个Gemini 3 Pro API Key
    "openai_claude": [...],      # Claude API Key
    "deepseek": [...],           # DeepSeek API Key
    "siliconflow": [...],        # 硅基流动 Key
    "other_models": [...]       # 其他模型 Key
  },
  "model_selection": {
    "strategy": "gemini_pro_priority"
  }
}
```

## 🎮 支持的模式

| 模式 | 命令 | 主要模型 | 用途 |
|------|------|---------|------|
| 研究 | `op -m` | Gemini 3 Pro | 深度分析、长文本处理 |
| 编程 | `op -c` | Claude 3.5 | 代码生成、调试修复 |
| 极速 | `op -f` | Groq/备用 | 快速响应、简单查询 |
| 吞吐 | `op -w` | DeepSeek/豆包 | 大批量处理 |
| 中文 | `op -cn` | 硅基流动/豆包 | 中文优化任务 |

## 🛡️ 故障处理

系统具备多层故障转移机制：
1. **Primary Pool故障** → 自动切换到Secondary Pool
2. **Secondary Pool故障** → 自动切换到Emergency Pool (OpenRouter)
3. **连接失败** → Pre-flight检查检测并跳过不可用API
4. **429限流** → 自动进入10分钟冷静期

## 📈 监控和统计

- **实时健康检查**: 每次API调用前1.5秒超时检测
- **使用统计**: 记录成功/失败次数、响应时间
- **成本跟踪**: 不同模型的使用成本分析
- **状态缓存**: API状态持久化，避免重复检测

---

**系统已达到商业级标准，可立即投入生产使用！** 🎉