"""
Contains event name to transformer method mapping.
"""
from eventtracking.processors.caliper import transformers

EVENT_MAPPING = {
    # Enrollment Events
    'edx.course.enrollment.activated': transformers.edx_course_enrollment,
    'edx.course.enrollment.deactivated': transformers.edx_course_enrollment,

    # Problem interaction events
    'edx.problem.completed': transformers.problem_transformer,
    'edx.grades.problem.submitted': transformers.problem_transformer,
    'problem_check': transformers.problem_transformer,
    'showanswer': transformers.problem_transformer,
    'edx.problem.hint.demandhint_displayed': transformers.problem_transformer,


    # Video events
    # These events are mapped to different names.

    # edx.video.loaded
    'load_video': transformers.load_stop_video,
    # 'edx.video.played'
    'play_video': transformers.play_pause_video,
    # 'edx.video.stopped'
    'stop_video': transformers.load_stop_video,
    # 'edx.video.paused'
    'pause_video': transformers.play_pause_video,
    # 'edx.video.position.changed'
    'seek_video': transformers.seek_video,

    # Course navigation events
    'edx.ui.lms.sequence.outline.selected': '',  # TODO: cannot find/generate this event
                                                 #  can be found in code using edx.ui.lms.outline.selected
    'edx.ui.lms.sequence.next_selected': transformers.edx_ui_lms_sequence_selection,
    'edx.ui.lms.sequence.previous_selected': transformers.edx_ui_lms_sequence_selection,
    'edx.ui.lms.sequence.tab_selected': transformers.edx_ui_lms_sequence_selection,
    'edx.ui.lms.link_clicked': transformers.edx_ui_lms_sequence_selection,
}
