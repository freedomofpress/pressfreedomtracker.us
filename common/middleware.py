import time
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def page_time_middleware(get_response):
    def middleware(request):
        start_time = time.perf_counter_ns()

        response = get_response(request)

        duration = (time.perf_counter_ns() - start_time) // 1_000_000

        response['X-Page-Generation-Time-ms'] = duration
        if duration > settings.SLOW_PAGE_WARN_THRESHOLD:
            logger.warning(f'Slow page warning: {request.method} {request.path} duration: {duration}ms')
        elif duration > settings.SLOW_PAGE_LOG_THRESHOLD:
            logger.info(f'Slow page notice: {request.method} {request.path} duration: {duration}ms')
        return response

    return middleware
