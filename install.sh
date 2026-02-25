#!/bin/bash

# OpenCode 智能模型调度系统 - 一键安装脚本
# 自动配置所有依赖和权限
# Author: Smart Model Dispatcher Team

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# 打印消息函数
print_header() {
    echo -e "${BLUE}${BOLD}🚀 OpenCode 智能模型调度系统 - 一键安装${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "\n${BOLD}📦 步骤 $1: $2${NC}"
}

# 检查系统环境
check_system() {
    print_step "1" "检查系统环境"
    
    # 检查操作系统
    if [[ "$OSTYPE" != "darwin"* ]] && [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "此脚本主要为 macOS 和 Linux 设计"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python 3 已安装 (版本: $PYTHON_VERSION)"
        
        # 使用Python进行版本比较
        if python3 -c "import sys; exit(0 if tuple(map(int, sys.argv[1].split('.'))) >= (3, 8) else 1)" "$PYTHON_VERSION"; then
            echo "Python版本检查通过"
        else
            print_error "需要 Python 3.8 或更高版本"
            exit 1
        fi
    else
        print_error "Python 3 未安装，请先安装 Python 3"
        exit 1
    fi
    
    # 检查jq
    if command -v jq &> /dev/null; then
        print_success "jq 已安装"
    else
        print_warning "jq 未安装，正在安装..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                brew install jq
            else
                print_error "请先安装 Homebrew 或手动安装 jq"
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Ubuntu/Debian
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y jq
            # CentOS/RHEL
            elif command -v yum &> /dev/null; then
                sudo yum install -y jq
            else
                print_error "无法自动安装 jq，请手动安装"
                exit 1
            fi
        fi
    fi
}

# 安装Python依赖
install_python_deps() {
    print_step "2" "安装Python依赖"
    
    # 进入项目目录
    cd "$(dirname "$0")"
    
    # 检查是否存在虚拟环境
    if [[ ! -d "venv" ]]; then
        print_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    print_info "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "Python依赖安装完成"
    else
        print_info "创建requirements.txt并安装依赖..."
        cat > requirements.txt << EOF
requests>=2.31.0
python-dotenv>=1.0.0
typing-extensions>=4.7.0
EOF
        pip install -r requirements.txt
        print_success "Python依赖安装完成"
    fi
}

# 配置文件权限
setup_permissions() {
    print_step "3" "配置文件权限"
    
    # 确保配置目录存在
    mkdir -p "$HOME/.config/opencode"
    mkdir -p "$HOME/.local/share/opencode"
    
    # 设置正确的文件权限
    if [[ -f "$HOME/.config/opencode/opencode.json" ]]; then
        chmod 600 "$HOME/.config/opencode/opencode.json"
        print_success "opencode.json 权限已设置为 600"
    fi
    
    if [[ -f "$HOME/.local/share/opencode/auth.json" ]]; then
        chmod 600 "$HOME/.local/share/opencode/auth.json"
        print_success "auth.json 权限已设置为 600"
    fi
    
    # 设置脚本执行权限
    chmod +x op
    chmod +x smart_model_dispatcher.py
    print_success "脚本执行权限已设置"
}

# 创建符号链接
create_symlinks() {
    print_step "4" "创建命令行快捷方式"
    
    # 询问是否创建全局符号链接
    read -p "是否创建全局命令 'op'？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        # 尝试创建到/usr/local/bin
        if [[ -w "/usr/local/bin" ]] || sudo -n true 2>/dev/null; then
            REAL_PATH=$(realpath op)
            if [[ -w "/usr/local/bin" ]]; then
                ln -sf "$REAL_PATH" "/usr/local/bin/op"
            else
                sudo ln -sf "$REAL_PATH" "/usr/local/bin/op"
            fi
            print_success "全局命令 'op' 已创建"
        else
            print_warning "无法创建全局符号链接，请手动添加到PATH"
            print_info "当前脚本路径: $(realpath op)"
            print_info "请将以下行添加到 ~/.zshrc 或 ~/.bashrc:"
            echo "export PATH=\"$(dirname $(realpath op)):\$PATH\""
        fi
    fi
}

# 验证安装
verify_installation() {
    print_step "5" "验证安装"
    
    # 检查文件是否存在
    local files=("op" "smart_model_dispatcher.py" "requirements.txt")
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "✓ $file"
        else
            print_error "✗ $file 不存在"
            return 1
        fi
    done
    
    # 测试命令帮助
    print_info "测试 op 命令..."
    if ./op help > /dev/null 2>&1; then
        print_success "✓ op 命令正常"
    else
        print_error "✗ op 命令异常"
        return 1
    fi
    
    # 检查OpenCode配置
    if [[ -f "$HOME/.config/opencode/opencode.json" ]]; then
        print_success "✓ OpenCode配置文件存在"
    else
        print_warning "⚠ OpenCode配置文件不存在，请先运行: opencode auth login"
    fi
    
    if [[ -f "$HOME/.local/share/opencode/auth.json" ]]; then
        print_success "✓ OpenCode认证文件存在"
    else
        print_warning "⚠ OpenCode认证文件不存在，请先运行: opencode auth login"
    fi
}

# 显示使用说明
show_usage() {
    echo -e "\n${BOLD}🎉 安装完成！${NC}"
    echo -e "\n${BLUE}快速开始:${NC}"
    echo "  op -m              # 激活研究模式 (Gemini 3 Pro 优先)"
    echo "  op -s              # 激活极速模式 (Groq/硅基流动优先)"
    echo "  op -c              # 激活编程模式 (Gemini/七牛云编程专用)"
    echo "  op -h              # 激活重载模式 (豆包/七牛云大Token)"
    echo "  op -cn             # 激活中文模式 (硅基流动/豆包优先)"
    echo "  op -e              # 激活紧急模式 (OpenRouter熔断器)"
    echo ""
    echo "  op smart \"任务描述\"  # 智能选择Profile"
    echo "  op status          # 查看系统状态"
    echo "  op health          # 执行健康检查"
    echo ""
    echo -e "${BLUE}核心特性:${NC}"
    echo "  • 静默自愈 - API故障自动切换"
    echo "  • 冷静期管理 - 429限流自动冷却"
    echo "  • 智能负载均衡 - 响应时间优化"
    echo "  • 紧急熔断 - OpenRouter终极备选"
    echo "  • 权限安全 - chmod 600 保护API密钥"
    echo ""
    echo -e "${BLUE}更多信息:${NC}"
    echo "  项目目录: $(pwd)"
    echo "  配置文件: $HOME/.config/opencode/opencode.json"
    echo "  认证文件: $HOME/.local/share/opencode/auth.json"
    echo "  状态文件: $HOME/.config/opencode/enhanced_api_status.json"
}

# 主函数
main() {
    print_header
    
    # 保存当前目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    # 执行安装步骤
    check_system
    install_python_deps
    setup_permissions
    create_symlinks
    verify_installation
    
    # 显示使用说明
    show_usage
    
    print_success "🎉 OpenCode 智能模型调度系统安装完成！"
}

# 错误处理
trap 'print_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"