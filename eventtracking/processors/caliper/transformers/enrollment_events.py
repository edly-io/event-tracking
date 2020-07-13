"""
Transformers for enrollment related events.
"""
from django.conf import settings
from django.urls import reverse


def edx_course_enrollment(current_event, caliper_event):
    """
    This transformer transformes two events:
        - edx.course.enrollment.activated
            Generated when a user is enrolled in a course.

        - edx.course.enrollment.deactivated
            Generated when a user is unenrolled from a course.
    """
    event = current_event['event'].copy()
    event.pop('user_id')

    course_root_url = '{root_url}{course_root}'.format(
        root_url=settings.LMS_ROOT_URL,
        course_root=reverse('course_root', kwargs={'course_id': event['course_id']})
    )

    caliper_event['object'].update({
        'id': course_root_url,
        'type': 'Membership',
        'extensions': event
    })

    caliper_event.update({
        'action': 'Activated' if (
            current_event['name'] == 'edx.course.enrollment.activated'
        ) else 'Deactivated',
        'type': 'Event',
    })

    return caliper_event
