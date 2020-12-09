"""
This module provides a fast api server. Currently only for prometheus
"""
import contextlib
import threading
import time
from multiprocessing import Process
from collections import namedtuple

import uvicorn
from fastapi import FastAPI
from .prometheus import make_asgi_app


app = FastAPI()


app.mount("/metrics", make_asgi_app())


class Server(uvicorn.Server):
    def __init__(self, config: uvicorn.Config):
        super().__init__(config=config)
        self.thread = None

    def t_start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        while not self.started:
            time.sleep(1e-3)

    def t_end(self):
        self.should_exit = True
        self.thread.join()

    def install_signal_handlers(self) -> None:
        pass

    @contextlib.contextmanager
    def context_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
