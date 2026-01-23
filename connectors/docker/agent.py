import json
import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from urllib.parse import quote

import psutil
import requests
import websocket


def env_bool(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


def log(message: str) -> None:
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] {message}", flush=True)


def _truncate(value: str, max_chars: int) -> str:
    if not value:
        return value
    return value[:max_chars]


def _build_ws_url(api_base: str, token: str) -> str:
    if api_base.startswith("https://"):
        ws_base = "wss://" + api_base[len("https://") :]
    elif api_base.startswith("http://"):
        ws_base = "ws://" + api_base[len("http://") :]
    else:
        ws_base = "ws://" + api_base
    return f"{ws_base}/agent/ws?token={quote(token)}"


def _send_command_ack(
    api_base: str,
    token: str,
    verify_ssl: bool,
    command_id: str,
    status: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    started_at: str,
    finished_at: str,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "command_id": command_id,
        "status": status,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "started_at": started_at,
        "finished_at": finished_at,
    }
    try:
        response = requests.post(
            f"{api_base}/agent/command-ack",
            headers=headers,
            json=payload,
            timeout=10,
            verify=verify_ssl,
        )
        response.raise_for_status()
    except Exception as exc:
        log(f"Command ack failed: {exc}")


def _execute_command(
    api_base: str,
    token: str,
    verify_ssl: bool,
    command_id: str,
    command: str,
    timeout_seconds: int,
    max_output_chars: int,
) -> None:
    started_at = datetime.utcnow().isoformat()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        stdout = _truncate(result.stdout or "", max_output_chars)
        stderr = _truncate(result.stderr or "", max_output_chars)
        status = "completed" if result.returncode == 0 else "failed"
        _send_command_ack(
            api_base,
            token,
            verify_ssl,
            command_id,
            status,
            result.returncode,
            stdout,
            stderr,
            started_at,
            datetime.utcnow().isoformat(),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _truncate(exc.stdout or "", max_output_chars)
        stderr = _truncate(exc.stderr or "Command timed out", max_output_chars)
        _send_command_ack(
            api_base,
            token,
            verify_ssl,
            command_id,
            "failed",
            124,
            stdout,
            stderr,
            started_at,
            datetime.utcnow().isoformat(),
        )
    except Exception as exc:
        _send_command_ack(
            api_base,
            token,
            verify_ssl,
            command_id,
            "failed",
            1,
            "",
            _truncate(str(exc), max_output_chars),
            started_at,
            datetime.utcnow().isoformat(),
        )


def _start_command_listener(
    api_base: str,
    token: str,
    verify_ssl: bool,
    timeout_seconds: int,
    max_output_chars: int,
) -> None:
    ws_url = _build_ws_url(api_base, token)

    def on_message(_, message: str) -> None:
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            return
        if payload.get("type") != "command":
            return
        command_id = payload.get("command_id")
        command = payload.get("command")
        if not command_id or not command:
            return
        threading.Thread(
            target=_execute_command,
            args=(
                api_base,
                token,
                verify_ssl,
                command_id,
                command,
                timeout_seconds,
                max_output_chars,
            ),
            daemon=True,
        ).start()

    def on_error(_, error: Exception) -> None:
        log(f"WebSocket error: {error}")

    def on_close(_, status_code, message) -> None:
        log(f"WebSocket closed: {status_code} {message}")

    def on_open(_) -> None:
        log("WebSocket connected for command channel.")

    while True:
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        ws.run_forever(sslopt=None if verify_ssl else {"cert_reqs": 0})
        time.sleep(5)


def main() -> int:
    api_base = os.getenv("PLATFORM_API_URL", "http://localhost:8000/api/v1").rstrip("/")
    token = os.getenv("AGENT_TOKEN")
    if not token:
        log("Missing AGENT_TOKEN env var.")
        return 1

    heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
    verify_ssl = env_bool("SSL_VERIFY", True)
    collect_stats = env_bool("COLLECT_SYSTEM_STATS", True)
    command_timeout = int(os.getenv("COMMAND_TIMEOUT", "60"))
    max_output_chars = int(os.getenv("MAX_OUTPUT_CHARS", "20000"))
    log(f"Starting agent with API base: {api_base}")
    log(f"Heartbeat interval: {heartbeat_interval}s, collect_stats={collect_stats}")
    log(f"Command timeout: {command_timeout}s, max_output_chars={max_output_chars}")
    log(f"SSL verify enabled: {verify_ssl}")

    auth_url = f"{api_base}/agent/authenticate"
    heartbeat_url = f"{api_base}/agent/heartbeat"

    try:
        auth_response = requests.post(
            auth_url,
            json={"token": token},
            timeout=10,
            verify=verify_ssl,
        )
        auth_response.raise_for_status()
        agent_info = auth_response.json()
        system_name = agent_info.get("system_name", "unknown")
        log(f"Agent authenticated for system: {system_name}")
    except Exception as exc:
        log(f"Failed to authenticate agent token: {exc}")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()

    command_thread = threading.Thread(
        target=_start_command_listener,
        args=(api_base, token, verify_ssl, command_timeout, max_output_chars),
        daemon=True,
    )
    command_thread.start()

    while True:
        metrics = {
            "agent_uptime_seconds": int(time.time() - start_time),
            "agent_timestamp": datetime.utcnow().isoformat(),
        }
        if collect_stats:
            metrics.update(
                {
                    "cpu_percent": psutil.cpu_percent(interval=0.2),
                    "cpu_count": psutil.cpu_count(logical=True) or 0,
                    "load_avg_1m": os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0,
                    "mem_total_bytes": psutil.virtual_memory().total,
                    "mem_used_bytes": psutil.virtual_memory().used,
                    "mem_used_percent": psutil.virtual_memory().percent,
                    "disk_total_bytes": psutil.disk_usage("/").total,
                    "disk_used_bytes": psutil.disk_usage("/").used,
                    "disk_used_percent": psutil.disk_usage("/").percent,
                }
            )

        payload = {
            "status": "connected",
            "metrics": metrics,
        }
        try:
            response = requests.post(
                heartbeat_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10,
                verify=verify_ssl,
            )
            response.raise_for_status()
            log(f"Heartbeat ok: {response.json().get('status', 'unknown')}")
        except Exception as exc:
            log(f"Heartbeat failed: {exc}")

        time.sleep(heartbeat_interval)


if __name__ == "__main__":
    raise SystemExit(main())
