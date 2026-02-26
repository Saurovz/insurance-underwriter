import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import threading
import time
import subprocess
import socket

from python_a2a import run_server          # ✅ FIXED: correct import
from agents.books.server import build_books_server
from config import settings


def wait_for_port(port: int, host: str = "localhost", timeout: float = 30.0) -> bool:
    """Poll port until server accepts connections — replaces blind time.sleep()"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def start_agent_server():
    server = build_books_server()
    run_server(server, host="0.0.0.0", port=settings.BOOKS_AGENT_PORT)  # ✅ FIXED


if __name__ == "__main__":
    print("=" * 55)
    print("  📚  Personal Book Advisor — Starting Up")
    print("=" * 55)

    agent_thread = threading.Thread(target=start_agent_server, daemon=True)
    agent_thread.start()
    print(f"✅ Books Agent starting on port {settings.BOOKS_AGENT_PORT}...")

    print("⏳ Waiting for agent server to be ready...")
    ready = wait_for_port(settings.BOOKS_AGENT_PORT, timeout=30)

    if not ready:
        print("❌ Agent server did not start. Check errors above.")
        sys.exit(1)

    print(f"✅ Books Agent is live on port {settings.BOOKS_AGENT_PORT}")

    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "app.py")
    print(f"🌐 Launching Streamlit UI → {ui_path}")
    print("=" * 55)

    subprocess.run(
        [
            sys.executable, "-m", "streamlit", "run", ui_path,
            "--server.port", "8501",
            "--server.fileWatcherType", "none",  # ✅ FIXED: kills torch warning
        ],
        check=True,
    )
