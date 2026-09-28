"""CP4 — Graceful shutdown.

Khi orchestrator gửi SIGTERM (Docker stop, K8s eviction, Cloud Run scale-down),
ta cần:
  1. Đánh dấu shutting_down = True → /health và /ready trả 503
     → load balancer ngừng đẩy request mới vào instance này.
  2. Nhường lại cho handler cũ (uvicorn) để server thực sự dừng.
  3. Rồi mới cho process thoát.
"""

from __future__ import annotations

import signal
import threading


class Lifecycle:
    def __init__(self) -> None:
        self.shutting_down: bool = False
        self._installed: bool = False
        self._lock = threading.Lock()
        self._previous: dict = {}

    def install(self) -> None:
        """Đăng ký handler cho SIGTERM / SIGINT. Idempotent."""
        if self._installed:
            return
        with self._lock:
            if self._installed:
                return
            for sig in (signal.SIGTERM, signal.SIGINT):
                try:
                    self._previous[sig] = signal.getsignal(sig)
                    signal.signal(sig, self.request_shutdown)
                except ValueError:
                    # Không phải main thread — bỏ qua, vẫn cho app chạy.
                    pass
            self._installed = True

    def request_shutdown(self, signum=None, frame=None) -> None:
        """Handler cho SIGTERM / SIGINT. Chỉ bật cờ, rồi nhường lại handler cũ."""
        self.shutting_down = True
        previous = self._previous.get(signum)
        if callable(previous):
            previous(signum, frame)


lifecycle = Lifecycle()