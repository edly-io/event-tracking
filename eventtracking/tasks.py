import logging
import pickle

from pickle import UnpicklingError
from celery.utils.log import get_task_logger

from celery import task


LOG = get_task_logger(__name__)


@task(name='eventtracking.tasks.async_send')
def async_send(backend_name, pickled_backend, event):

    try:
        backend = pickle.loads(pickled_backend)
    except UnpicklingError:
        raise ValueError('Cannot initialize backend %s' % backend_name)

    try:
        backend.send(event)
    except Exception:  # pylint: disable=broad-except
        LOG.exception(
            'Unable to send event to backend: %s', backend_name
        )
