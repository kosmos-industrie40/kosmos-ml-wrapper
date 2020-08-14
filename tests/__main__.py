""" TODO: Please write a docstring """
import logging

# from ml_wrapper import MLWrapper
from tests.mock_ml_function import FFT

logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    mlw = FFT()
    num_of_processes = mlw.thread_pool._processes
    mlw.logger.info("Pool:" + str(mlw.thread_pool._pool))
    mlw.logger.info("Processes:" + str(mlw.thread_pool._processes))
    mlw.logger.info("Taskqueue:" + str(mlw.thread_pool._taskqueue))
    mlw.logger.info("ctx:" + str(mlw.thread_pool._ctx.__dict__))
    mlw.logger.info("inqueue:" + str(mlw.thread_pool._inqueue))
    mlw.logger.info("state:" + str(mlw.thread_pool._state))
    mlw.start()
