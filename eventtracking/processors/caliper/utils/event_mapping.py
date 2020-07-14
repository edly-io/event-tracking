"""
Contains event name to transformer method mapping.
"""
from eventtracking.processors.caliper import transformers

EVENT_MAPPING = {
    # Enrollment Events
    'edx.course.enrollment.activated': transformers.edx_course_enrollment,
    'edx.course.enrollment.deactivated': transformers.edx_course_enrollment,

    # Problem interaction events
    'edx.problem.completed': transformers.edx_problem_completed,
    'edx.grades.problem.submitted': transformers.edx_grades_problem_submitted,
    'problem_check': transformers.problem_check,
    'showanswer': transformers.show_answer,
    'edx.problem.hint.demandhint_displayed': transformers.edx_problem_hint_demandhint_displayed,


    # Video events
    # These events are mapped to different names.

    # edx.video.loaded
    'load_video': transformers.video_transformer,
    # 'edx.video.played'
    'play_video': transformers.video_transformer,
    # 'edx.video.stopped'
    'stop_video': transformers.video_transformer,
    # 'edx.video.paused'
    'pause_video': transformers.video_transformer,
    # 'edx.video.position.changed'
    'seek_video': transformers.video_transformer,

    # Course navigation events
    'edx.ui.lms.sequence.outline.selected': '', # TODO: cannot find/generate this event
                                                #  can be found in code using edx.ui.lms.outline.selected
    'edx.ui.lms.sequence.next_selected': transformers.edx_ui_lms_sequence_selection,
    'edx.ui.lms.sequence.previous_selected': transformers.edx_ui_lms_sequence_selection,
    'edx.ui.lms.sequence.tab_selected': transformers.edx_ui_lms_sequence_selection,
    'edx.ui.lms.link_clicked': transformers.edx_ui_lms_sequence_selection,
}
