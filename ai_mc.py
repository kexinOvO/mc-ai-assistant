import requests
import json
import time
import re
import ssl
import urllib.request

API_KEY = "你的MCSM_API密钥"
INSTANCE_UUID = "你的实例UUID"
DAEMON_ID = "你的守护进程ID"
API_BASE = "https://你的MCSM地址"

AI_API_KEY = "你的AI_API密钥"
AI_BASE_URL = "https://api.openai.com/v1"
AI_MODEL = "gpt-3.5-turbo"

BLACKLIST_COMMANDS = [
    "stop", "restart", "reload",
    "kick", "ban", "pardon", "ban-ip", "pardon-ip",
    "op", "deop",
    "whitelist", "whitelist add", "whitelist remove", "whitelist reload",
    "kill @e", "kill @a",
    "tp @a", "spreadplayers @a",
    "execute",
    "plugin", "plugins",
    "timings", "spark", "lag",
    "backup",
]

last_log = ""
processed_lines = set()

def get_log():
    global last_log
    try:
        url = f"{API_BASE}/api/protected_instance/outputlog"
        params = {
            "uuid": INSTANCE_UUID,
            "daemonId": DAEMON_ID,
            "apikey": API_KEY
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=utf-8"
        }
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            log_data = json.loads(r.text)['data']
            if log_data != last_log:
                last_log = log_data
                return log_data.splitlines()
    except Exception as e:
        print(f"[错误] 获取日志失败: {e}")
    return []

def send_command(command):
    try:
        url = f"{API_BASE}/api/protected_instance/command"
        params = {
            "uuid": INSTANCE_UUID,
            "daemonId": DAEMON_ID,
            "apikey": API_KEY,
            "command": command
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json; charset=utf-8"
        }
        r = requests.post(url, headers=headers, params=params, json={}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[错误] 发送命令失败: {e}")
        return False

def is_command_blocked(command):
    cmd_lower = command.lower().strip()
    for blocked in BLACKLIST_COMMANDS:
        if cmd_lower.startswith(blocked):
            return True
    return False

def get_ai_response(question, player):
    url = f"{AI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """你是Minecraft AI助手。你只能执行常规游戏操作命令。

玩家请求执行操作时，返回JSON：
{"type":"command","command":"..."}

玩家只是问问题时，返回JSON：
{"type":"chat","reply":"..."}

你必须严格遵守：
1. 只返回上述两种JSON格式
2. command只包含一条MC命令，不带斜杠开头（如 "give Kexin torch 64"）
3. 不要执行任何管理类命令（禁止：stop, restart, kick, ban, op, deop, whitelist, kill @a, kill @e, tp @a, gamerule, worldborder等）

玩家名字是：""" + player

    data = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
            result = json.loads(response.read().decode('utf-8'))
            reply = result['choices'][0]['message']['content']
            try:
                return json.loads(reply)
            except:
                return {"type": "chat", "reply": reply}
    except Exception as e:
        return {"type": "chat", "reply": f"AI请求失败: {e}"}

def execute_command(command):
    if is_command_blocked(command):
        print(f"[安全拦截] {command}")
        return False
    return send_command(command)

def main():
    print("=" * 50)
    print("Minecraft AI 助手 (MCSM API 模式)")
    print(f"实例UUID: {INSTANCE_UUID}")
    print(f"AI模型: {AI_MODEL}")
    print(f"黑名单: {len(BLACKLIST_COMMANDS)} 条危险命令")
    print("=" * 50)
    print("\n监听中... (输入 '@AI xxx' 触发)")
    print("按 Ctrl+C 退出\n")

    initial_lines = get_log()
    for line in initial_lines:
        processed_lines.add(line)
    send_command("say AI助手已上线!")

    while True:
        lines = get_log()
        for line in lines:
            if line in processed_lines:
                continue
            processed_lines.add(line)

            match = re.search(r"\[.*?\]: <(.+?)> (.+)", line)
            if match:
                player = match.group(1)
                msg = match.group(2)

                if msg.startswith("@AI"):
                    question = msg[3:].strip()
                    print(f"\n[{player}] {question}")

                    result = get_ai_response(question, player)

                    if result["type"] == "command":
                        cmd = result["command"]
                        print(f"[执行] /{cmd}")
                        if execute_command(cmd):
                            print(f"[成功]")
                            send_command(f"say [AI] 已完成: {cmd}")
                        else:
                            print(f"[失败]")
                            send_command("say [AI] 命令执行失败")
                    else:
                        reply = result["reply"]
                        print(f"[回复] {reply}")
                        send_command(f"say [AI] {reply}")

        time.sleep(2)

if __name__ == "__main__":
    main()
