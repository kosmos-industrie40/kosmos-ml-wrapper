"""
This module provides a fast api server. Currently only for prometheus
"""
import contextlib
import threading
import time

import uvicorn
from fastapi import FastAPI

from prometheus_client import make_asgi_app


# Declare Fastapi app and set it up
app = FastAPI()
app.mount("/metrics", make_asgi_app())


class Server(uvicorn.Server):
    """
    This subclass of uvicorns Server class allows the server to be properly run in a threaded mode
    """

    def __init__(self, config: uvicorn.Config):
        super().__init__(config=config)
        self.thread = None

    def t_start(self):
        """
        Start server in thread. Don't forget to call t_end to close the thread
        """
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        while not self.started:
            time.sleep(1e-3)

    def t_end(self):
        """
        End the server's Thread
        """
        self.should_exit = True
        self.thread.join()

    def install_signal_handlers(self) -> None:
        """
        Overwrite parent's threading
        """

    @contextlib.contextmanager
    def context_thread(self):
        """
        Provide a context based threading
        """
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
