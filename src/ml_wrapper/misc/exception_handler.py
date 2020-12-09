import traceback
from logging import Logger

from ml_wrapper.messaging.state_message import StateMessage, ToolState


def handle_exception(
    exception: Exception,
    logger: Logger,
    state: StateMessage = None,
    raise_further: bool = False,
) -> bool:
    """
    Hanldes an exception separately and eases the settings for it
    :param exception: The exception to handle
    :param logger: The logger to print the traceback on
    :param state: The state object of the ml wrapper
    :param raise_further: Flag to tell the tool whether to raise the exception or not
    """
    logger.info(
        "The application caught a wild exception!"
        f"Your settings tell me {'not' if raise_further else ''} to raise this exception."
    )
    logger.error(exception.__traceback__)
    traceback.print_tb(exception.__traceback__)
    if state is not None:
        state.state = ToolState.ERROR
    if raise_further:
        raise exception from exception
