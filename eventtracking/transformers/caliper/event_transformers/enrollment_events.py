"""
Transformers for enrollment related events.
"""
from django.conf import settings
from django.urls import reverse

from eventtracking.transformers.caliper.base_transformer import CaliperTransformer
from eventtracking.transformers.caliper.registry import TransformerRegistry


@TransformerRegistry.register('edx.course.enrollment.activated')
@TransformerRegistry.register('edx.course.enrollment.deactivated')
class EnrollmentEventTransformers(CaliperTransformer):
    """
    This transformer transformes two events:
        - edx.course.enrollment.activated
            Generated when a user is enrolled in a course.

        - edx.course.enrollment.deactivated
            Generated when a user is unenrolled from a course.
    """

    type = 'Event'

    def get_action(self, event, _):
        """
        Return action for caliper event.
        """
        if event['name'] == 'edx.course.enrollment.activated':
            return 'Activated'
        return 'Deactivated'

    def get_object(self, current_event, _):
        """
        Return transformed object for caliper event.
        """
        data = current_event['data'].copy()
        data.pop('user_id')

        course_root_url = '{root_url}{course_root}'.format(
            root_url=settings.LMS_ROOT_URL,
            course_root=reverse('course_root', kwargs={'course_id': data['course_id']})
        )
        caliper_object = {
            'id': course_root_url,
            'type': 'Membership',
            'extensions': data
        }
        return caliper_object
