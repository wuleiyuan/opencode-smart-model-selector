#!/bin/bash

# OpenCode 智能包装脚本 v2.2 (TUI Edition)
# 核心特性：SSL 证书穿透 + 终端直启模式 + 智能模型调度

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }

# 获取目录 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_DISPATCHER="$SCRIPT_DIR/smart_model_dispatcher.py"
OP_CMD="$SCRIPT_DIR/op.sh"

# 自动定位 opencode 真身（穿透 alias） 
OP_BIN=$(which opencode 2>/dev/null | head -n 1)

# Python 路径 
if [[ -f "$SCRIPT_DIR/venv/bin/python3" ]]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON_CMD="python3"
fi

# 核心启动函数 - 安全版
launch_opencode() {
    print_success "🚀 正在终端启动 OpenCode (TUI)..."
    
    # 方案1: 正确配置系统 CA 证书 (推荐)
    # 如果使用代理软件 (Surge/Clash)，将其 CA 证书加入系统信任
    # macOS: 钥匙串访问 → 导入证书 → 始终信任
    
    # 方案2: 指定自定义 CA 证书 (适用于特定代理)
    # export NODE_EXTRA_CA_CERTS="/path/to/proxy-ca.pem"
    
    # 方案3: 保留验证但禁用代理 SSL 检验 (调试用)
    # 仅在排查问题时临时使用，完成后应删除
    if [[ "$DEBUG_TLS" == "1" ]]; then
        print_info "⚠️ 调试模式: 临时禁用 SSL 验证 (不安全!)"
        env NODE_TLS_REJECT_UNAUTHORIZED=0 command "$OP_BIN" "$@"
    else
        # 正常启动 - 保留完整 SSL 验证
        command "$OP_BIN" "$@"
    fi
}

# 主逻辑控制 
main() {
    case "${1:-}" in
        "run")
            launch_opencode
            ;;
        "design"|"pm"|"frontend"|"backend"|"fast")
            # 调用你的 Python 调度引擎 
            "$PYTHON_CMD" "$SMART_DISPATCHER" $([[ "$1" == "backend" ]] && echo "crawler" || echo "coding")
            launch_opencode
            ;;
        "smart")
            # 调用模型选择器进行 AI 分析 
            shift
            "$OP_CMD" smart "$@"
            launch_opencode
            ;;
        "clear")
            rm -f "$HOME/.config/opencode/.task_context"
            print_success "上下文已清理"
            ;;
        *)
            # 默认：检测任务后启动 
            launch_opencode
            ;;
    esac
}

main "$@"