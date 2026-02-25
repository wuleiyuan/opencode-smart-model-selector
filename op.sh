#!/bin/bash

# OpenCode 智能模型调度系统 V1.0
# 修复版 - 动态路径 + 代理沙箱 + venv 支持

# [修复 1] 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/smart_model_dispatcher.py"

# [修复 2] 优先使用虚拟环境的 Python
if [[ -f "$SCRIPT_DIR/venv/bin/python3" ]]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON_CMD="python3"
fi

CONFIG_FILE="$HOME/.config/opencode/oh-my-opencode.json"
FALLBACK_CONFIG="$HOME/.config/opencode/opencode.json"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# 激活Profile
activate_profile() {
    local profile="$1"
    
    case "$profile" in
        "-m"|"main"|"research")
            print_info "🧠 激活研究模式 (Google Gemini Pro 轮询)"
            "$PYTHON_CMD" "$PYTHON_SCRIPT" research
            ;;
        "-c"|"coding"|"coding")
            print_info "💻 激活编程模式 (Claude 3.5/3.7)"
            "$PYTHON_CMD" "$PYTHON_SCRIPT" coding
            ;;
        "-f"|"fast"|"fast")
            print_info "⚡ 激活极速模式 (免费模型优先)"
            "$PYTHON_CMD" "$PYTHON_SCRIPT" fast
            ;;
        "-w"|"crawler"|"crawler")
            print_info "📦 激活吞吐模式 (DeepSeek/豆包)"
            "$PYTHON_CMD" "$PYTHON_SCRIPT" crawler
            ;;
        "-cn"|"chinese"|"cn")
            print_info "🇨🇳 激活中文模式 (硅基流动/MiniMax)"
            "$PYTHON_CMD" "$PYTHON_SCRIPT" cn
            ;;
        *)
            print_error "未知Profile: $profile"
            echo "可用: -m(research), -c(coding), -f(fast), -w(crawler), -cn(chinese)"
            exit 1
            ;;
    esac
}

# 显示当前配置
show_current() {
    print_info "当前OpenCode配置:"
    
    local config_file=""
    if [[ -f "$CONFIG_FILE" ]]; then
        config_file="$CONFIG_FILE"
    elif [[ -f "$FALLBACK_CONFIG" ]]; then
        config_file="$FALLBACK_CONFIG"
    fi
    
    if [[ -n "$config_file" ]]; then
        local model=$(jq -r '.model // .agents.oracle.model // "未设置"' "$config_file" 2>/dev/null)
        echo "   模型: $model"
        echo "   配置文件: $config_file"
    else
        print_error "配置文件不存在"
    fi
}

# 全自动智能模式：根据任务描述自动选择并切换模型
auto_smart_mode() {
    local task="$*"
    if [[ -z "$task" ]]; then
        print_error "请提供任务描述"
        echo "用法: op <任务描述>"
        echo "示例: op 帮我写一个 Python 排序算法"
        exit 1
    fi
    
    print_info "🧠 全自动智能分析任务..."
    
    # 获取模型推荐结果
    local result=$("$PYTHON_CMD" "$SCRIPT_DIR/model_selector.py" --auto "$task" 2>&1)
    echo "$result"
    
    # 提取推荐的提供商 (provider/xxx 格式)
    local provider=$(echo "$result" | grep -E "^🏢 提供商:" | sed 's/🏢 提供商: *//' | xargs | tr '[:upper:]' '[:lower:]')
    local model=$(echo "$result" | grep -E "^🎯 推荐模型:" | sed 's/🎯 推荐模型: *//' | xargs)
    
    print_info "🎯 自动切换到: $provider ($model)"
    
    # 根据提供商映射到对应的profile并激活
    case "$provider" in
        *"google"*)
            "$PYTHON_CMD" "$PYTHON_SCRIPT" research
            ;;
        *"siliconflow"*)
            "$PYTHON_CMD" "$PYTHON_SCRIPT" fast
            ;;
        *"deepseek"*)
            "$PYTHON_CMD" "$PYTHON_SCRIPT" crawler
            ;;
        *"anthropic"*)
            "$PYTHON_CMD" "$PYTHON_SCRIPT" coding
            ;;
        *"qwen"*)
            "$PYTHON_CMD" "$PYTHON_SCRIPT" fast
            ;;
        *)
            print_info "使用 research 默认模式..."
            "$PYTHON_CMD" "$PYTHON_SCRIPT" research
            ;;
    esac
}

# 显示帮助
show_help() {
    echo "OpenCode 智能模型调度系统 v2.5 (全自动模式)"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  🎯 全自动模式 (推荐)：直接输入任务，自动选择最优模型"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  op <任务描述>              AI自动分析并切换模型"
    echo "  示例: op 写一个Python快速排序算法"
    echo "  示例: op 翻译这段英文到中文"
    echo "  示例: op 分析这段代码的性能问题"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  📋 手动模式：显式指定模式"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  op -m              研究模式 (Google Gemini Pro)"
    echo "  op -c              编程模式 (Claude 3.5/3.7)"
    echo "  op -f              极速模式 (免费模型优先)"
    echo "  op -w              吞吐模式 (DeepSeek/豆包)"
    echo "  op -cn             中文模式 (硅基流动/MiniMax)"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  🤖 守护进程模式 (后台自动监控)"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  op daemon start    启动后台守护进程 (自动选择模型 + 故障转移)"
    echo "  op daemon stop    停止守护进程"
    echo "  op daemon status  查看守护进程状态"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  📊 状态管理"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  op current         显示当前配置"
    echo "  op help            显示此帮助"
    echo ""
    echo "✨ 智能特性:"
    echo "  🤖 全自动：无需输入命令，直接描述任务"
    echo "  🎯 Gemini Pro 付费为主"
    echo "  💰 免费 API 为辅"
    echo "  🔧 其他付费次之"
    echo "  🧠 最大化利用模型特长"
    echo "  🔄 故障自动转移 (守护进程模式)"
}

# 检测是否是任务描述（不以 - 开头，看起来像自然语言）
is_task_description() {
    local first_arg="$1"
    # 如果第一个参数以 - 开头，或者是已知命令，则是手动模式
    if [[ "$first_arg" == -* ]]; then
        return 1
    fi
    # 如果是已知命令词
    case "$first_arg" in
        "smart"|"-s"|"--smart"|"current"|"help"|"-h"|"--help"|"main"|"coding"|"fast"|"crawler"|"chinese"|"research")
            return 1
            ;;
    esac
    # 看起来像任务描述
    return 0
}

# 主逻辑
main() {
    # 检测是否是全自动模式（直接提供任务描述）
    if is_task_description "${1:-}"; then
        # 全自动模式：直接分析任务
        auto_smart_mode "$@"
        return
    fi
    
    case "${1:-}" in
        "-m"|"--main"|"main"|"research")
            activate_profile "research"
            ;;
        "-c"|"--coding"|"coding")
            activate_profile "coding"
            ;;
        "-f"|"--fast"|"fast")
            activate_profile "fast"
            ;;
        "-w"|"--crawler"|"crawler")
            activate_profile "crawler"
            ;;
        "-cn"|"--chinese"|"chinese"|"cn")
            activate_profile "cn"
            ;;
        "smart"|"-s"|"--smart")
            # 智能模式（兼容旧命令）
            shift
            if [[ -z "${1:-}" ]]; then
                print_error "请提供任务描述"
                echo "用法: op smart <任务描述>"
                echo "示例: op smart 帮我写一个 Python 排序算法"
                exit 1
            fi
            auto_smart_mode "$@"
            ;;
        "current")
            show_current
            ;;
        "daemon")
            shift
            case "${1:-}" in
                "start")
                    print_info "启动守护进程..."
                    "$PYTHON_CMD" "$SCRIPT_DIR/daemon.py" start
                    ;;
                "stop")
                    print_info "停止守护进程..."
                    "$PYTHON_CMD" "$SCRIPT_DIR/daemon.py" stop
                    ;;
                "status")
                    "$PYTHON_CMD" "$SCRIPT_DIR/daemon.py" status
                    ;;
                *)
                    print_error "用法: op daemon [start|stop|status]"
                    exit 1
                    ;;
            esac
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"