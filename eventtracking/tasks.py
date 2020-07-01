"""
Celery tasks
"""

import json

from celery.utils.log import get_task_logger
from celery import task

from eventtracking.helpers import BackendJSONDecoder


LOG = get_task_logger(__name__)


@task(name='eventtracking.tasks.async_send')
def async_send(json_backend, event):
    """
    Task to load provided json backend and call it's send to process event asynchronously
    :param json_backend:
    :param event:
    """

    try:
        backend = json.loads(json_backend, cls=BackendJSONDecoder)
    except ValueError:
        LOG.exception(
            'JSONDecodeError: Unable to decode: %s', json_backend
        )

    backend.send(event)
