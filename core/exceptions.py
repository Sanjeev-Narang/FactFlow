from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Wraps all DRF errors in a consistent shape:
    {
        "error": {
            "status_code": 400,
            "detail": { ... }
        }
    }
    Every error from every endpoint looks the same.
    Frontend never has to guess the error structure.
    """
    response = exception_handler(exc, context)

    if response is None:
        logger.critical(str(exc), exc_info=True)
    elif response.status_code >= 500:
        logger.error(str(exc), exc_info=True)
    else:
        logger.warning(str(exc), exc_info=True)

    if response is not None:
        response.data = {
            "error": {
                "status_code": response.status_code,
                "detail": response.data,
            }
        }

    return response