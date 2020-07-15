"""
Transformers for video interaction events.
"""
from datetime import timedelta

from isodate import duration_isoformat

from eventtracking.transformers.caliper.base_transformer import CaliperTransformer
from eventtracking.transformers.caliper.registry import TransformerRegistry


EVENTS_ACTION_MAP = {
    'load_video': 'Retrieved',
    'play_video': 'Started',
    'stop_video': 'Ended',
    'complete_video': 'Ended',
    'pause_video': 'Paused',
    'seek_video': 'JumpedTo',
}


def make_video_block_id(video_id, course_id, video_block_name='video+block', block_version='block-v1'):
    """
    Return formatted video block id for provided video and course.
    """
    return '{block_version}:{course_id}+type@{video_block_name}@{video_id}'.format(
        block_version=block_version,
        course_id=course_id,
        video_block_name=video_block_name,
        video_id=video_id
    )


def convert_seconds_to_iso(seconds):
    """
    Convert seconds from integer to ISO format.
    """
    return duration_isoformat(timedelta(
        seconds=seconds
    ))


class BaseVideoTransformer(CaliperTransformer):
    """
    Base transformer for video interaction events.
    """
    type = 'MediaEvent'

    def get_action(self, current_event, _):
        """
        Return action for the caliper event.
        """
        return EVENTS_ACTION_MAP[current_event['name']]

    def get_object(self, current_event, caliper_event):
        """
        Return object for the caliper event.
        """
        self.json_load_event()
        caliper_object = caliper_event['object']
        event = current_event['data'].copy()

        course_id = current_event['context']['course_id']
        video_id = event['id']

        object_id = make_video_block_id(course_id=course_id, video_id=video_id)

        caliper_object.update({
            'id': object_id,
            'type': 'VideoObject',
            'duration': duration_isoformat(timedelta(
                    seconds=event.pop('duration')
            ))
        })

        return caliper_object

    def transform(self):
        """
        Override the base class transform method to clean unwanted
        fields from the transformed event.
        """
        transformed_event = super().transform()
        if 'duration' in transformed_event['object']['extensions']:
            del transformed_event['object']['extensions']['duration']
        return transformed_event


@TransformerRegistry.register('load_video')
class LoadVideoTransformer(BaseVideoTransformer):
    """
    Transform "load_video" event.
    """
    type = 'Event'

    def get_object(self, current_event, caliper_event):
        """
        Return transformed object for the caliper event.
        """
        caliper_object = super(LoadVideoTransformer, self).get_object(current_event, caliper_event)

        caliper_event['object']['extensions'].update(current_event['data'])
        return caliper_object


@TransformerRegistry.register('stop_video')
@TransformerRegistry.register('complete_video')
class StopVideoTransformer(BaseVideoTransformer):
    """
    Transform "stop_video" and "complete_video" events.

    Please note that "complete_video" doesn't exist currently but is
    expected to be added.
    """

    def get_object(self, current_event, caliper_event):
        """
        Return transformed object for the caliper event.
        """
        caliper_object = super(StopVideoTransformer, self).get_object(current_event, caliper_event)
        event = current_event['data'].copy()

        if 'currentTime' in event:
            caliper_object['extensions']['currentTime'] = convert_seconds_to_iso(event.pop('currentTime'))

        caliper_object['extensions'].update(event)
        return caliper_object


@TransformerRegistry.register('play_video')
@TransformerRegistry.register('pause_video')
class PlayPauseVideoTransformer(BaseVideoTransformer):
    """
    Transform "play_video" and "pause_video" events.
    """
    transforming_fields = BaseVideoTransformer.transforming_fields + ('target', )

    def get_object(self, current_event, caliper_event):
        """
        Return transformed object for the caliper event.
        """
        caliper_object = super(PlayPauseVideoTransformer, self).get_object(current_event, caliper_event)

        event = current_event['data'].copy()

        if 'currentTime' in event:
            del event['currentTime']

        caliper_object['extensions'].update(event)
        return caliper_object

    def get_target(self, current_event, caliper_event):
        """
        Return target for the caliper event.
        """
        current_time = convert_seconds_to_iso(
            seconds=current_event['data']['currentTime']
        )

        return {
            'id': caliper_event['object']['id'],
            'type': 'MediaLocation',
            'currentTime': current_time
        }


@TransformerRegistry.register('seek_video')
class SeekVideoTransformer(BaseVideoTransformer):
    """
    Transform "seek_video" event.
    """

    def get_object(self, current_event, caliper_event):
        """
        Return tranformed object for the caliper event.
        """
        caliper_object = super().get_object(current_event, caliper_event)
        event = current_event['data'].copy()

        new_time = convert_seconds_to_iso(
            seconds=event.pop('new_time')
        )
        old_time = convert_seconds_to_iso(
            seconds=event.pop('old_time')
        )
        caliper_object['extensions'].update({
            'new_time': new_time,
            'old_time': old_time
        })

        caliper_object['extensions'].update(event)
        return caliper_object
