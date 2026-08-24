#!/usr/bin/env python3
"""
AgencyOS Unified Microservices & Backend Supervisor.
Uses only Python Standard Library (no external dependencies needed for supervisor).
Spawns, monitors, and manages all backend microservices:
  - Lead Finder (Port 8000)
  - SDR Microservice (Port 8081)
  - Lead Manager (Port 8082)
  - Communication Service / Gmail Listener (Port 8083)
  - Voice Agent (Port 8084)
"""

import json
import os
import select
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
VENV_UVICORN = REPO_ROOT / ".venv" / "bin" / "uvicorn"

PYTHON_BIN = (
    str(VENV_UVICORN)
    if VENV_UVICORN.exists()
    else (str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable)
)

SERVICES = [
    {
        "name": "Lead Finder",
        "key": "leadfinder",
        "port": 8000,
        "app": "MicroServices.Lead_Finder.main:app",
        "cwd": str(REPO_ROOT),
        "env": {
            "PYTHONPATH": f"{REPO_ROOT}:{REPO_ROOT / 'MicroServices'}:{REPO_ROOT / 'MicroServices/leadfinder'}:{os.environ.get('PYTHONPATH', '')}"
        },
        "health_path": "/health",
    },
    {
        "name": "SDR Intelligence",
        "key": "sdr",
        "port": 8081,
        "app": "MicroServices.SDR.server:app",
        "cwd": str(REPO_ROOT),
        "env": {
            "PYTHONPATH": f"{REPO_ROOT}:{REPO_ROOT / 'MicroServices'}:{os.environ.get('PYTHONPATH', '')}"
        },
        "health_path": "/health",
    },
    {
        "name": "Lead Manager",
        "key": "lead_manager",
        "port": 8082,
        "app": "MicroServices.Lead_Manager.main:app",
        "cwd": str(REPO_ROOT),
        "env": {
            "PYTHONPATH": f"{REPO_ROOT}:{REPO_ROOT / 'MicroServices'}:{os.environ.get('PYTHONPATH', '')}"
        },
        "health_path": "/health",
    },
    {
        "name": "Communication Service",
        "key": "communication",
        "port": 8083,
        "app": "app.main:app",
        "cwd": str(REPO_ROOT / "services" / "gmail_pubsub_listener"),
        "env": {
            "PYTHONPATH": f"{REPO_ROOT / 'services' / 'gmail_pubsub_listener'}:{os.environ.get('PYTHONPATH', '')}"
        },
        "health_path": "/health",
    },
    {
        "name": "Voice Agent",
        "key": "voice_agent",
        "port": 8084,
        "app": "MicroServices.Voice_Agent.server:app",
        "cwd": str(REPO_ROOT),
        "env": {
            "PYTHONPATH": f"{REPO_ROOT}:{REPO_ROOT / 'MicroServices'}:{os.environ.get('PYTHONPATH', '')}"
        },
        "health_path": "/health",
    },
]


def kill_existing_on_port(port: int):
    """Clean up any process already listening on the given port."""
    try:
        res = subprocess.run(["fuser", f"{port}/tcp"], capture_output=True, text=True)
        pids = res.stdout.strip().split()
        for pid in pids:
            if pid and pid != str(os.getpid()):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
    except Exception:
        pass


def start_service(svc):
    env = os.environ.copy()
    env.update(svc.get("env", {}))

    # Check if uvicorn binary exists, otherwise run module with python
    if VENV_UVICORN.exists():
        cmd = [
            str(VENV_UVICORN),
            svc["app"],
            "--host",
            "0.0.0.0",
            "--port",
            str(svc["port"]),
            "--log-level",
            "info",
        ]
    else:
        cmd = [
            str(VENV_PYTHON if VENV_PYTHON.exists() else sys.executable),
            "-m",
            "uvicorn",
            svc["app"],
            "--host",
            "0.0.0.0",
            "--port",
            str(svc["port"]),
            "--log-level",
            "info",
        ]

    proc = subprocess.Popen(
        cmd,
        cwd=svc["cwd"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def check_health(svc):
    url = f"http://127.0.0.1:{svc['port']}{svc['health_path']}"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "AgencyOS-Supervisor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=2.5) as response:
            if response.status == 200:
                body = response.read().decode("utf-8")
                try:
                    return True, json.loads(body)
                except Exception:
                    return True, body
            return False, f"Status code: {response.status}"
    except urllib.error.URLError as e:
        return False, str(e.reason if hasattr(e, "reason") else e)
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 80)
    print(" 🚀 STARTING ALL AGENCYOS MICROSERVICES & BACKEND")
    print("=" * 80)
    print(f"[*] Workspace Root : {REPO_ROOT}")
    print(f"[*] Python Runtime : {PYTHON_BIN}")
    print("=" * 80)

    # First clean up any lingering stale processes on the ports
    for svc in SERVICES:
        kill_existing_on_port(svc["port"])

    time.sleep(0.5)

    processes = {}
    for svc in SERVICES:
        print(f"[*] Launching {svc['name']} on http://0.0.0.0:{svc['port']}...")
        proc = start_service(svc)
        processes[svc["key"]] = (svc, proc)

    print("\n[*] Waiting for services to initialize...")
    time.sleep(3)

    print("\n" + "=" * 80)
    print(" 🔍 HEALTH CHECK DASHBOARD")
    print("=" * 80)

    for svc in SERVICES:
        healthy, detail = check_health(svc)
        status_icon = "✅ ONLINE" if healthy else "⏳ PENDING / ERROR"
        detail_str = json.dumps(detail) if isinstance(detail, dict) else str(detail)
        print(
            f" {status_icon:18} | {svc['name']:25} | Port {svc['port']} | {detail_str[:45]}"
        )

    print("=" * 80)
    print(
        "[*] All microservices are active. Streaming logs (Press Ctrl+C to stop)...\n"
    )

    streams = {
        proc.stdout: svc["name"] for _, (svc, proc) in processes.items() if proc.stdout
    }

    try:
        while True:
            # Check if any process has exited unexpectedly
            for key, (svc, proc) in processes.items():
                ret = proc.poll()
                if ret is not None:
                    print(
                        f"[!] Warning: {svc['name']} (PID {proc.pid}) exited with code {ret}"
                    )

            # Read available output from non-blocking pipes
            if streams:
                rlist, _, _ = select.select(list(streams.keys()), [], [], 0.5)
                for s in rlist:
                    try:
                        line = s.readline()
                        if line:
                            name = streams.get(s, "SERVICE")
                            print(f"[{name}] {line.rstrip()}", flush=True)
                    except Exception:
                        pass
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[*] Received shutdown signal. Terminating all microservices...")
        for key, (svc, proc) in processes.items():
            print(f"[*] Stopping {svc['name']} (PID: {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("[*] All microservices stopped successfully.")


if __name__ == "__main__":
    main()
