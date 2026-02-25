#!/bin/zsh
# OpenCode 自动启动脚本 (支持 Zsh 和 Bash)

SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
OPENCODE_DAEMON_SCRIPT="$SCRIPT_DIR/daemon.py"
OPENCODE_PID_FILE="$HOME/.config/opencode/daemon.pid"
OPENCODE_PROJECT_DIR="$SCRIPT_DIR"

is_daemon_running() {
    if [[ -f "$OPENCODE_PID_FILE" ]]; then
        local pid=$(cat "$OPENCODE_PID_FILE" 2>/dev/null)
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

start_opencode_daemon() {
    if [[ -f "$OPENCODE_DAEMON_SCRIPT" ]]; then
        cd "$OPENCODE_PROJECT_DIR"
        nohup python3 "$OPENCODE_DAEMON_SCRIPT" daemon >/dev/null 2>&1 &
        sleep 1
    fi
}

opencode_auto_start() {
    if [[ "$PWD" == "$OPENCODE_PROJECT_DIR"* ]]; then
        if ! is_daemon_running; then
            start_opencode_daemon
        fi
    fi
}

# Zsh 模式
if [[ -n "$ZSH_VERSION" ]]; then
    opencode_auto_start
    autoload -Uz add-zsh-hook
    add-zsh-hook chpwd opencode_auto_start

# Bash 模式
elif [[ -n "$BASH_VERSION" ]]; then
    # Bash 兼容: 使用 PROMPT_COMMAND 模拟目录切换检测
    LAST_PWD="$PWD"
    
    opencode_auto_start_bash() {
        if [[ "$PWD" != "$LAST_PWD" ]]; then
            LAST_PWD="$PWD"
            opencode_auto_start
        fi
    }
    
    # 避免重复添加
    if [[ -z "$OPENCODE_AUTO_STARTED" ]]; then
        export OPENCODE_AUTO_STARTED=1
        PROMPT_COMMAND="opencode_auto_start_bash; $PROMPT_COMMAND"
    fi

else
    echo "⚠️ 此脚本需要 Zsh 或 Bash"
    exit 1
fi
