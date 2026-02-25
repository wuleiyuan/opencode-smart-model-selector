# API Configuration Template

## 📋 Configuration Instructions

This file has been **cleaned for security**. Add your actual API keys below following the specified formats.

## 🔑 API Key Formats

### Google AI Studio (Gemini)
```json
"gemini_pro_paid": [
  "AIzaSyDum_your_actual_key_here_1234567890"
]
```
- **Format**: Starts with `AIzaSyDum`, 20-100 characters
- **Get keys**: https://aistudio.google.com/app/apikey
- **Usage**: Primary model (Gemini 2.0 Pro)

### Anthropic Claude
```json
"openai_claude": [
  "sk-ant-your_actual_claude_key_here_123456789012345678901234567890"
]
```
- **Format**: Starts with `sk-ant`, 40+ characters
- **Get keys**: https://console.anthropic.com/
- **Usage**: Code generation and expert tasks

### DeepSeek
```json
"deepseek": [
  "sk-de2bd_your_actual_deepseek_key_here"
]
```
- **Format**: Starts with `sk-de2bd`, exactly 32 characters
- **Get keys**: https://platform.deepseek.com/
- **Usage**: Cost-effective alternative

### SiliconFlow
```json
"siliconflow": [
  "sk-yyeh_your_actual_siliconflow_key_here_123456789012345678901234567890123456"
]
```
- **Format**: Starts with `sk-yyeh`, 40+ characters
- **Get keys**: https://siliconflow.cn/
- **Usage**: Chinese language optimization

### MiniMax
```json
"other_models": [
  "7697b0a1_your_actual_minimax_key_here"
]
```
- **Format**: Starts with `7697b0a1`, 20+ characters
- **Usage**: High-throughput scenarios

## 🛡️ Security Notes

- **Never commit** real API keys to version control
- **Use environment variables** for production deployments
- **Rotate keys regularly** for better security
- **Monitor usage** to detect unauthorized access

## 🚀 Quick Start

1. Copy this template to `api_config.json`
2. Add your API keys in the appropriate sections
3. Run: `python3 smart_model_dispatcher.py research`

## 📞 Support

For issues with the smart model selector, check the system logs or run with verbose output.