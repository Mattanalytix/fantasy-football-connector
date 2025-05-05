import os
import logging
from functools import wraps
from typing import Callable, Any
from dotenv import load_dotenv

# Cloud Logging imports
from google.cloud.logging_v2.handlers import StructuredLogHandler


def setup_logging() -> None:
    """
    Configure logging based on the environment.
    This function sets up logging configuration based on whether the
    application is running in a local development environment or in
    Google Cloud. It ensures proper log formatting and handling for
    both environments.

    Returns:
        None

    Environment Variables:
        LOCAL_ENV: If set to "true", configures local logging. Otherwise,
                   sets up Google Cloud structured logging.
    """
    # Load env vars from .env in local dev
    load_dotenv()

    # Choose logging mode
    if os.getenv("LOCAL_ENV") == "true":
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
        logging.info("Local logging initialized.")
    else:
        # Use StructuredLogHandler to avoid threading shutdown issues
        handler = StructuredLogHandler()
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Ensure log handler is flushed and closed on shutdown
        import atexit
        atexit.register(handler.flush)
        atexit.register(handler.close)
        logging.info("Google Cloud structured logging initialized.")


def with_logging(main_func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to automatically set up logging for a function.

    This decorator wraps a function and ensures that logging is properly
    configured before the function executes. It uses the setup_logging function
    to configure logging based on the environment (local or Google Cloud).

    Args:
        main_func: The function to be decorated. This function will have
                   logging automatically configured before it runs.

    Returns:
        Callable: The wrapped function with logging configured.

    Usage:
        @with_logging
        def my_function():
            # Function code here
            pass
    """
    @wraps(main_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        setup_logging()
        return main_func(*args, **kwargs)

    return wrapper
