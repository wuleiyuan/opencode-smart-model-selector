"""
OpenCode Smart Model Selector 版本管理模块

版本号格式: MAJOR.MINOR.PATCH
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的新功能
- PATCH: 向后兼容的 bug 修复
"""

__version__ = "2.2.0"
__author__ = "OpenCode Team"
__description__ = "智能模型调度系统"

VERSION_HISTORY = {
    "1.0.0": {
        "date": "2025-01-01",
        "description": "初始版本 - 智能模型选择 + 故障转移"
    },
    "2.0.0": {
        "date": "2025-02-25", 
        "description": "重大更新: 手动指定模型 > 自动推荐优先级 (24h TTL, 连续3次失败自动切换), 添加 op auto/reset 命令, 长文本降级策略, 测速记忆持久化"
    },
    "2.1.0": {
        "date": "2026-02-26",
        "description": "新增功能: API Server 模块 (OpenAI 兼容接口), op api 命令"
    },
    "2.2.0": {
        "date": "2026-02-27",
        "description": "新增功能: 双引擎架构, 熔断降级, 并发优化, 测速缓存4h过期, op engine 命令"
    }
}

def get_version():
    return __version__

def get_version_info():
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "history": VERSION_HISTORY
    }

def print_version():
    print(f"OpenCode Smart Model Selector v{__version__}")
    print(f"Author: {__author__}")
    print()
    print("版本历史:")
    for ver, info in VERSION_HISTORY.items():
        print(f"  v{ver} ({info['date']}) - {info['description'][:50]}...")

if __name__ == "__main__":
    print_version()
