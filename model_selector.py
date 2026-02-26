#!/usr/bin/env python3
"""
智能模型选择器 v1.0
根据任务类型智能选择最优模型，并自动切换

优先级策略：
1. Gemini Pro 付费 (最高优先级)
2. 免费 API (Google Gemini Flash, SiliconFlow 等)
3. 其他付费 API (Claude, GPT-4 等)

Author: OpenCode AI Assistant
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 颜色输出
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    
    @staticmethod
    def cyan(s): return f"{Colors.CYAN}{s}{Colors.RESET}"
    @staticmethod
    def green(s): return f"{Colors.GREEN}{s}{Colors.RESET}"
    @staticmethod
    def yellow(s): return f"{Colors.YELLOW}{s}{Colors.RESET}"
    @staticmethod
    def magenta(s): return f"{Colors.MAGENTA}{s}{Colors.RESET}"
    @staticmethod
    def bold(s): return f"{Colors.BOLD}{s}{Colors.RESET}"

# 直接 import dispatcher
sys.path.insert(0, str(Path(__file__).parent))
from smart_model_dispatcher import SmartModelDispatcher


class TaskType(Enum):
    """任务类型枚举"""
    CODING = "coding"           # 编程开发
    ANALYSIS = "analysis"        # 代码分析
    DEBUGGING = "debugging"     # 调试排错
    WRITING = "writing"         # 文档写作
    TRANSLATION = "translation" # 翻译
    CHAT = "chat"              # 日常对话
    RESEARCH = "research"       # 研究查询
    CREATIVE = "creative"      # 创意内容
    MATH = "math"              # 数学计算
    GENERAL = "general"         # 通用任务


class Priority(Enum):
    """模型优先级"""
    TIER_1 = 1  # Gemini Pro 付费 (最高)
    TIER_2 = 2  # 免费模型
    TIER_3 = 3  # 其他付费


@dataclass
class Model:
    """模型配置"""
    id: str
    name: str
    provider: str
    priority: Priority
    strengths: List[str]      # 擅长领域
    weaknesses: List[str]     # 不擅长领域
    cost_per_1k_tokens: float
    context_window: int
    speed: str               # fast/medium/slow
    available: bool = True


class TaskAnalyzer:
    """任务类型分析器 - 支持中英文关键词"""
    
    # 任务类型关键词 (优化中文支持)
    _PATTERN_STRINGS = {
        TaskType.CODING: [
            r'(code|编程|函数|class|def|import|api|算法|implement|refactor|写代码|写一个|写个|写个函数|写段代码|写程序|代码|程序|开发)',
            r'\b(write|create|build|develop|make)\s+(code|program|function|app|tool)\b',
            r'\.(py|js|ts|java|cpp|c|go|rs|jsx|tsx|vue|swift)$',
            r'(排序|算法|函数|类|接口|模块|前端|后端|全栈|web|app|脚本)',
        ],
        TaskType.ANALYSIS: [
            r'\b(analyze|analysis|review)\b',
            r'\b(code|project|system|architecture)\s+(review|analysis|audit)\b',
            r'(分析|检查|审查|解释|理解|代码审查|性能分析|优化建议)',
        ],
        TaskType.DEBUGGING: [
            r'\b(debug|error|bug|fix|crash|exception|fail)\b',
            r"\b(Not working|doesn't work|broken|wrong)\b",
            r'Traceback|Exception|Error|Stack trace',
            r'(错误|修复|崩溃|问题|bug|调试|报错|闪退|卡死)',
        ],
        TaskType.WRITING: [
            r'\b(write|create|draft|compose)\s+(doc|article|post|blog|readme|email)\b',
            r'\b(summarize|rewrite|edit|improve|polish)\b',
            r'\.(md|txt|doc|rst)$',
            r'(写文章|写文档|写README|写博客|写报告|总结|改写)',
        ],
        TaskType.TRANSLATION: [
            r'\b(translate|translation|convert)\b',
            r'\b中文|英文|Japanese|Korean|French|German|Spanish\b',
            r'(翻译|什么意思|怎么写|如何说)',
        ],
        TaskType.CHAT: [
            r'^hi|^hello|^hey',
            r"\b(what's up|how are you)\b",
            r'^(!|\?|)[a-zA-Z\s]{0,20}$',
            r'(你好|在吗|嗨|hey|hi|hello|聊聊)',
        ],
        TaskType.RESEARCH: [
            r'\b(research|find|search|lookup|look up)\b',
            r'\b(latest|newest|recent|2024|2025|2026)\b',
            r'\b(compare|versus|vs|pros and cons)\b',
            r'(搜索|查找|研究|对比|比较|区别|哪个好)',
        ],
        TaskType.CREATIVE: [
            r'\b(create|generate|design|imagine)\s+(story|poem|song|idea|concept)\b',
            r'\b(creative|original|innovative)\b',
            r'\b(brainstorm)\b',
            r'(创意|头脑风暴|写故事|写诗|创作|设计|想象)',
        ],
        TaskType.MATH: [
            r'\b(calculate|compute|solve)\s+(equation|integral|derivative|math)\b',
            r'[+\-*/^%=|<>]',
            r'\d+[\d,\.]*\d*[\+\-\*/]\d+[\d,\.]*\d*',
            r'(计算|数学|方程|积分|微分|算一下)',
        ],
    }
    
    # 预编译所有正则表达式
    PATTERNS = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in _PATTERN_STRINGS.items()}
    
    # 复杂度指标 (预编译)
    _COMPLEXITY_STRINGS = [
        r'\b(complex|difficult|hard|advanced|expert|professional)\b',
        r'\b(architecture|system design|microservice|distributed)\b',
        r'\b(optimization|performance|scalability)\b',
        r'\b(500|1000|10000)\+',
        r'\b(million|billion|trillion)\b',
        r'\b(multi-|cross-|poly-)\b',
        r'(复杂|困难|高级|专家|架构|系统设计|微服务|分布式|优化|性能|高并发)',
    ]
    COMPLEXITY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _COMPLEXITY_STRINGS]
    
    # 紧急任务指标 (预编译)
    _URGENT_STRINGS = [
        r'\b(urgent|ASAP|immediately|now|quick|fast)\b',
        r'\b(before|deadline|due)\b',
        r'\b(broken|critical|emergency|help)\b',
        r'(紧急|马上|立刻|立即|着急|deadline|截止|崩溃|严重|救命)',
    ]
    URGENT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _URGENT_STRINGS]
    
    def __init__(self, task: str):
        self.task = task.lower()
    
    def classify(self) -> TaskType:
        """分析任务类型"""
        scores = {}
        
        for task_type, compiled_patterns in self.PATTERNS.items():
            score = 0
            for pattern in compiled_patterns:
                if pattern.search(self.task):
                    score += 1
            scores[task_type] = score
        
        best_type = max(scores, key=lambda k: scores[k])
        
        if scores[best_type] == 0:
            return TaskType.GENERAL
        return best_type
    
    def get_complexity(self) -> float:
        """评估任务复杂度 (0.0 - 1.0)"""
        score = 0
        for pattern in self.COMPLEXITY_PATTERNS:
            if pattern.search(self.task):
                score += 0.15
        
        return min(1.0, score)
    
    def is_urgent(self) -> bool:
        """是否紧急任务"""
        for pattern in self.URGENT_PATTERNS:
            if pattern.search(self.task):
                return True
        return False


class APIHealthChecker:
    """API 健康检查器 - 快速检查模型可用性"""
    
    # Provider 端点配置
    PROVIDER_ENDPOINTS = {
        "google": ("https://generativelanguage.googleapis.com/v1beta/models?key={key}", "google_api_key"),
        "anthropic": ("https://api.anthropic.com/v1/models", "anthropic_api_key"),
        "deepseek": ("https://api.deepseek.com/v1/models", "deepseek_api_key"),
        "siliconflow": ("https://api.siliconflow.cn/v1/models", "siliconflow_api_key"),
        "openai": ("https://api.openai.com/v1/models", "openai_api_key"),
    }
    
    def __init__(self, cache_ttl: int = 60):
        """初始化
        
        Args:
            cache_ttl: 缓存有效期(秒)，默认60秒
        """
        import time
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = cache_ttl
        self._cache_time: Dict[str, float] = {}
    
    def _load_api_keys(self) -> Dict[str, str]:
        """从 auth.json 加载 API keys"""
        import json
        from pathlib import Path
        
        auth_config = Path.home() / ".local" / "share" / "opencode" / "auth.json"
        if not auth_config.exists():
            return {}
        
        try:
            with open(auth_config, 'r') as f:
                data = json.load(f)
        except Exception:
            return {}
        
        # 转换 provider_map
        key_map = {}
        for provider, (_, key_name) in self.PROVIDER_ENDPOINTS.items():
            if key_name in data:
                key_map[provider] = data[key_name]
        
        return key_map
    
    def check_provider(self, provider: str) -> bool:
        """检查单个 provider 是否可用"""
        import time
        import requests
        
        # 检查缓存
        if provider in self._cache:
            if time.time() - self._cache_time.get(provider, 0) < self._cache_ttl:
                return self._cache[provider]
        
        # 加载 keys
        keys = self._load_api_keys()
        api_key = keys.get(provider)
        
        if not api_key:
            self._cache[provider] = False
            self._cache_time[provider] = time.time()
            return False
        
        # 快速健康检查 (2秒超时)
        endpoint, _ = self.PROVIDER_ENDPOINTS.get(provider, ("", ""))
        if not endpoint:
            return False
        
        try:
            if "{key}" in endpoint:
                url = endpoint.format(key=api_key)
                response = requests.get(url, timeout=2)
            else:
                headers = {"Authorization": f"Bearer {api_key}"}
                response = requests.get(url, headers=headers, timeout=2)
            
            is_healthy = response.status_code == 200
            self._cache[provider] = is_healthy
            self._cache_time[provider] = time.time()
            return is_healthy
        except Exception:
            self._cache[provider] = False
            self._cache_time[provider] = time.time()
            return False
    
    def get_available_providers(self) -> Dict[str, bool]:
        """获取所有 provider 的可用状态"""
        return {provider: self.check_provider(provider) 
                for provider in self.PROVIDER_ENDPOINTS.keys()}


class SmartModelSelector:
    """智能模型选择器 - 支持动态 API 可用性"""
    
    # 模型配置
    MODELS = {
        # Tier 1: Gemini Pro 付费 (最高优先级)
        "gemini-1.5-pro": Model(
            id="gemini-1.5-pro",
            name="Gemini 1.5 Pro",
            provider="google",
            priority=Priority.TIER_1,
            strengths=["coding", "analysis", "reasoning", "long-context", "multimodal"],
            weaknesses=["creative-writing"],
            cost_per_1k_tokens=0.0025,
            context_window=2000000,
            speed="medium",
        ),
        "gemini-2.0-pro": Model(
            id="gemini-2.0-pro",
            name="Gemini 2.0 Pro",
            provider="google",
            priority=Priority.TIER_1,
            strengths=["coding", "analysis", "reasoning", "long-context", "math", "science"],
            weaknesses=["creative"],
            cost_per_1k_tokens=0.003,
            context_window=2000000,
            speed="fast",
        ),
        
        # Tier 2: 免费模型
        "gemini-1.5-flash": Model(
            id="gemini-1.5-flash",
            name="Gemini 1.5 Flash",
            provider="google",
            priority=Priority.TIER_2,
            strengths=["fast", "chat", "translation", "simple-coding"],
            weaknesses=["deep-analysis", "complex-reasoning"],
            cost_per_1k_tokens=0.000075,
            context_window=1000000,
            speed="fast",
        ),
        "gemini-1.5-flash-8b": Model(
            id="gemini-1.5-flash-8b",
            name="Gemini 1.5 Flash-8B",
            provider="google",
            priority=Priority.TIER_2,
            strengths=["fast", "simple-tasks", "chat"],
            weaknesses=["complex-tasks"],
            cost_per_1k_tokens=0.000075,
            context_window=1000000,
            speed="fastest",
        ),
        "qwen-2.5-72b": Model(
            id="qwen-2.5-72b",
            name="Qwen 2.5 72B",
            provider="siliconflow",
            priority=Priority.TIER_2,
            strengths=["coding", "math", "chinese", "reasoning"],
            weaknesses=["english-creative"],
            cost_per_1k_tokens=0.00014,
            context_window=131072,
            speed="fast",
        ),
        "deepseek-chat": Model(
            id="deepseek-chat",
            name="DeepSeek Chat",
            provider="deepseek",
            priority=Priority.TIER_2,
            strengths=["coding", "reasoning", "cost-effective"],
            weaknesses=["creative-writing"],
            cost_per_1k_tokens=0.00014,
            context_window=128000,
            speed="fast",
        ),
        
        # Tier 3: 其他付费模型
        "claude-3.5-sonnet": Model(
            id="claude-3.5-sonnet",
            name="Claude 3.5 Sonnet",
            provider="anthropic",
            priority=Priority.TIER_3,
            strengths=["coding", "analysis", "writing", "reasoning", "safety"],
            weaknesses=["speed"],
            cost_per_1k_tokens=0.015,
            context_window=200000,
            speed="medium",
        ),
        "claude-3.7-sonnet": Model(
            id="claude-3.7-sonnet",
            name="Claude 3.7 Sonnet",
            provider="anthropic",
            priority=Priority.TIER_3,
            strengths=["coding", "analysis", "complex-reasoning", "writing"],
            weaknesses=["speed"],
            cost_per_1k_tokens=0.015,
            context_window=200000,
            speed="medium",
        ),
        "gpt-4o": Model(
            id="gpt-4o",
            name="GPT-4o",
            provider="openai",
            priority=Priority.TIER_3,
            strengths=["multimodal", "coding", "analysis", "chat"],
            weaknesses=["cost"],
            cost_per_1k_tokens=0.01,
            context_window=128000,
            speed="medium",
        ),
        "gpt-4o-mini": Model(
            id="gpt-4o-mini",
            name="GPT-4o Mini",
            provider="openai",
            priority=Priority.TIER_3,
            strengths=["fast", "cost-effective", "simple-tasks"],
            weaknesses=["complex-reasoning"],
            cost_per_1k_tokens=0.0006,
            context_window=128000,
            speed="fast",
        ),
    }
    
    # 任务类型 -> 最佳模型匹配
    TASK_MODEL_MAP = {
        TaskType.CODING: [
            "gemini-2.0-pro",
            "claude-3.7-sonnet",
            "qwen-2.5-72b",
            "deepseek-chat",
            "gemini-1.5-pro",
        ],
        TaskType.ANALYSIS: [
            "gemini-2.0-pro",
            "claude-3.5-sonnet",
            "gpt-4o",
            "gemini-1.5-flash",
        ],
        TaskType.DEBUGGING: [
            "claude-3.7-sonnet",
            "gemini-2.0-pro",
            "deepseek-chat",
            "gpt-4o-mini",
        ],
        TaskType.WRITING: [
            "claude-3.5-sonnet",
            "gpt-4o",
            "gemini-1.5-pro",
        ],
        TaskType.TRANSLATION: [
            "gemini-1.5-flash",
            "qwen-2.5-72b",
            "deepseek-chat",
        ],
        TaskType.CHAT: [
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gpt-4o-mini",
        ],
        TaskType.RESEARCH: [
            "gemini-2.0-pro",
            "claude-3.5-sonnet",
            "gpt-4o",
        ],
        TaskType.CREATIVE: [
            "claude-3.5-sonnet",
            "gemini-1.5-pro",
            "gpt-4o",
        ],
        TaskType.MATH: [
            "gemini-2.0-pro",
            "qwen-2.5-72b",
            "deepseek-chat",
        ],
        TaskType.GENERAL: [
            "gemini-1.5-pro",
            "claude-3.5-sonnet",
            "gemini-1.5-flash",
        ],
    }
    
    def __init__(self, available_keys: Optional[Dict[str, bool]] = None, enable_health_check: bool = True):
        """初始化智能模型选择器
        
        Args:
            available_keys: 静态可用性配置 (可选)
            enable_health_check: 是否启用动态健康检查 (默认启用)
        """
        self._health_checker = APIHealthChecker() if enable_health_check else None
        self._static_available_keys = available_keys or {
            "google": True,
            "anthropic": True,
            "deepseek": True,
            "siliconflow": True,
            "openai": True,
        }
        
        # 初始化时获取动态健康状态
        self._dynamic_health: Dict[str, bool] = {}
        if self._health_checker:
            try:
                self._dynamic_health = self._health_checker.get_available_providers()
            except Exception:
                pass
        
        # 合并静态和动态可用性 (动态优先)
        for model_id, model in self.MODELS.items():
            provider = model.provider
            # 动态检查结果优先，否则使用静态配置
            if provider in self._dynamic_health:
                model.available = self._dynamic_health[provider]
            else:
                model.available = self._static_available_keys.get(provider, True)
    
    def select(self, task: str) -> Tuple[Model, str]:
        analyzer = TaskAnalyzer(task)
        task_type = analyzer.classify()
        complexity = analyzer.get_complexity()
        is_urgent = analyzer.is_urgent()
        
        # [成本优化] 长文本降级策略 - 超过 8000 tokens 自动切换免费模型
        estimated_tokens = len(task) // 4  # 粗略估算: 4 字符 ≈ 1 token
        LONG_TEXT_THRESHOLD = 8000
        
        # 只有非 coding 任务才触发长文本降级 (coding 需要高复杂度模型)
        if estimated_tokens > LONG_TEXT_THRESHOLD and task_type != TaskType.CODING:
            logger.info(f"📏 检测到长文本 ({estimated_tokens} tokens)，启用成本优化策略")
            # 优先选择免费长上下文模型
            free_long_context = ["gemini-1.5-flash", "qwen-2.5-72b"]
            for model_id in free_long_context:
                if model_id in self.MODELS and self.MODELS[model_id].available:
                    return self.MODELS[model_id], f"📏 长文本优化: {estimated_tokens} tokens > {LONG_TEXT_THRESHOLD}，自动降级到免费模型"
        
        candidates = self.TASK_MODEL_MAP.get(task_type, self.TASK_MODEL_MAP[TaskType.GENERAL])
        
        cost_sensitive_tasks = {TaskType.CHAT, TaskType.TRANSLATION, TaskType.GENERAL}
        is_cost_sensitive = task_type in cost_sensitive_tasks and not is_urgent and complexity < 0.5
        
        if complexity > 0.7:
            candidates = [c for c in candidates if self.MODELS.get(c, self.MODELS["gemini-1.5-pro"]).priority.value <= 2]
        elif is_urgent:
            speed_rank = {"fastest": 0, "fast": 1, "medium": 2}
            candidates = sorted(candidates, 
                            key=lambda c: speed_rank.get(self.MODELS.get(c, self.MODELS["gemini-1.5-flash"]).speed, 1))
        
        if is_cost_sensitive:
            candidates = sorted(
                candidates,
                key=lambda c: self.MODELS.get(c, self.MODELS["gemini-1.5-flash"]).cost_per_1k_tokens
            )
        
        for model_id in candidates:
            model = self.MODELS.get(model_id)
            if model and model.available:
                reason = self._generate_reason(task_type, complexity, model, is_cost_sensitive)
                return model, reason
        
        for model_id in candidates:
            model = self.MODELS.get(model_id)
            if model:
                reason = f"备选方案: {model.name}"
                return model, reason
        
        fallback = self.MODELS["gemini-1.5-flash"]
        return fallback, "兜底选择: 免费快速模型"
    
    def _generate_reason(self, task_type: TaskType, complexity: float, model: Model, is_cost_sensitive: bool = False) -> str:
        reasons = []
        
        if is_cost_sensitive:
            reasons.append(f"💰 成本优化：${model.cost_per_1k_tokens:.4f}/1K tokens")
        elif model.priority == Priority.TIER_1:
            reasons.append("🎯 首选：Gemini Pro 付费版")
        elif model.priority == Priority.TIER_2:
            reasons.append("💰 优化：免费模型，性价比高")
        else:
            reasons.append("🔧 专业：付费模型，功能最强")
        
        if task_type.value in model.strengths:
            reasons.append(f"✅ 擅长{task_type.value}任务")
        
        if complexity > 0.7:
            reasons.append("🧠 适配复杂任务")
        elif complexity < 0.3:
            reasons.append("⚡ 适合简单任务")
        
        if model.speed == "fastest":
            reasons.append("🚀 极速响应")
        elif model.speed == "fast":
            reasons.append("💨 快速响应")
        
        if model.cost_per_1k_tokens < 0.001:
            reasons.append("💵 零成本/低成本")
        elif model.cost_per_1k_tokens < 0.01:
            reasons.append("💵 低成本")
        
        return " | ".join(reasons)
    
    def list_models(self) -> List[Dict]:
        return [
            {
                "id": m.id,
                "name": m.name,
                "provider": m.provider,
                "priority": m.priority.name,
                "speed": m.speed,
                "cost_per_1k_tokens": m.cost_per_1k_tokens,
                "strengths": m.strengths,
                "available": m.available,
            }
            for m in self.MODELS.values()
        ]
    
    def get_profile_name(self, model: Model) -> str:
        profile_map = {
            "gemini-1.5-pro": "research",
            "gemini-2.0-pro": "research",
            "gemini-1.5-flash": "fast",
            "gemini-1.5-flash-8b": "fast",
            "claude-3.5-sonnet": "coding",
            "claude-3.7-sonnet": "coding",
            "deepseek-chat": "crawler",
            "qwen-2.5-72b": "cn",
            "gpt-4o": "coding",
            "gpt-4o-mini": "fast",
        }
        return profile_map.get(model.id, "research")
    
    def activate(self, task: str) -> bool:
        analyzer = TaskAnalyzer(task)
        task_type = analyzer.classify()
        
        model, reason = self.select(task)
        profile = self.get_profile_name(model)
        
        try:
            print(f"\n🤖 智能选择完成，正在切换到 {model.name}...")
            
            dispatcher = SmartModelDispatcher()
            success = dispatcher.activate_profile(profile)
            
            if success:
                print(f"\n✅ 切换成功！")
                print(f"🎯 模型: {model.name}")
                print(f"🏢 提供商: {model.provider}")
                print(f"💰 成本: ${model.cost_per_1k_tokens:.4f}/1K tokens")
                print(f"\n💡 {reason}")
                return True
            else:
                print(f"\n❌ 切换失败")
                return False
                
        except Exception as e:
            print(f"\n❌ 切换错误: {e}")
            return False


def main():
    json_output = False
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        json_output = True
        sys.argv.remove("--json")
    
    if len(sys.argv) < 2:
        if json_output:
            print(json.dumps({"error": "请提供任务描述"}))
            sys.exit(1)
        print("用法: python3 model_selector.py [选项] <任务描述>")
        print("")
        print("选项:")
        print("  --json     JSON 格式输出（供脚本调用）")
        print("")
        print("示例:")
        print("  python3 model_selector.py '帮我写一个 Python 排序算法'")
        print("  python3 model_selector.py --json '帮我翻译'")
        print("")
        print("中文关键词支持:")
        print("  编程: 写代码、写程序、写函数、开发")
        print("  分析: 分析、检查、审查、优化")
        print("  调试: 错误、修复、崩溃、bug")
        print("  写作: 写文档、写文章、写博客")
        print("  翻译: 翻译、什么意思、怎么写")
        print("  聊天: 你好、在吗、聊聊")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    selector = SmartModelSelector()
    model, reason = selector.select(task)
    
    if json_output:
        result = {
            "model": f"{model.provider}/{model.id}",
            "provider": model.provider,
            "name": model.name,
            "reason": reason,
            "cost_per_1k_tokens": model.cost_per_1k_tokens,
            "context_window": model.context_window,
            "speed": model.speed,
            "strengths": model.strengths,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    print(f"\n{Colors.magenta('🤖')} {Colors.bold('智能模型选择结果')}")
    print(Colors.cyan("=" * 60))
    print(f"{Colors.yellow('📝')} 任务: {task}")
    print(f"\n{Colors.green('🎯')} 推荐模型: {Colors.bold(model.name)}")
    print(f"{Colors.yellow('🏢')} 提供商: {model.provider}")
    print(f"{Colors.yellow('💰')} 成本: ${model.cost_per_1k_tokens:.4f}/1K tokens")
    print(f"{Colors.yellow('📏')} 上下文: {model.context_window:,} tokens")
    print(f"{Colors.yellow('🚀')} 速度: {model.speed}")
    print(f"\n{Colors.cyan('💡')} 选择理由: {reason}")
    print(f"\n{Colors.green('✅')} 擅长: {', '.join(model.strengths)}")
    print(Colors.cyan("=" * 60))
    print(f"\n{Colors.cyan('💡')} 提示: 直接使用 op.sh 自动切换")
    print(f"   示例: op '{task[:30]}...'")


if __name__ == "__main__":
    main()
