# Minecraft AI 助手

基于 MCSM API 和 AI 大模型的 Minecraft 服务器智能助手。

## 功能特性

- **实时日志监听**：通过 MCSM API 获取服务器日志，实时响应玩家消息
- **AI 智能对话**：玩家输入 `@AI xxx` 触发 AI 助手，支持问答和命令执行
- **安全黑名单**：内置危险命令黑名单，防止误执行管理类操作
- **双向通信**：支持在游戏内发送消息和执行命令

## 配置说明

使用前请在脚本中填写配置信息：

```python
API_KEY = "你的MCSM_API密钥"
INSTANCE_UUID = "你的实例UUID"
DAEMON_ID = "你的守护进程ID"
API_BASE = "https://你的MCSM地址"

AI_API_KEY = "你的AI_API密钥"
AI_BASE_URL = "https://api.openai.com/v1"
AI_MODEL = "gpt-3.5-turbo"
```

## 使用方法

1. 配置完成后，运行脚本：
   ```bash
   python ai_mc.py
   ```

2. 在游戏中，玩家发送消息：
   - `@AI 你好` - 与 AI 对话
   - `@AI 给我一个火把` - 请求执行命令（AI 会执行如 `give` 等常规命令）

3. 按 `Ctrl+C` 退出程序

## 黑名单命令

以下命令被拦截，不会执行：

- 管理类：`stop`, `restart`, `reload`, `kick`, `ban`, `pardon`, `op`, `deop`, `whitelist`
- 破坏类：`kill @e`, `kill @a`, `tp @a`, `spreadplayers @a`
- 其他危险操作：`execute`, `plugin`, `plugins`, `timings`, `spark`, `lag`, `backup`, `worldborder`

## AI 响应格式

AI 返回两种 JSON 格式：

1. **命令执行**：
   ```json
   {"type":"command","command":"give Kexin torch 64"}
   ```

2. **对话回复**：
   ```json
   {"type":"chat","reply":"你好！有什么可以帮助你的吗？"}
   ```

## 依赖

- Python 3.7+
- requests
- 标准库：`json`, `time`, `re`, `ssl`, `urllib.request`

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
