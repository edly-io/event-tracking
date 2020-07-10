"""
Contains event name to transformer method mapping.
"""
from eventtracking.processors.caliper import transformers

EVENT_MAPPING = {
    # Enrollment Events
    'edx.course.enrollment.activated': '',
    'edx.course.enrollment.deactivated': '',

    # Problem interaction events
    'edx.grades.problem.submitted': '',
    'problem_check': transformers.problem_check,
    'showanswer': '',
    'edx.problem.hint.demandhint_displayed': '',


    # Video events
    'edx.video.loaded': '',
    'edx.video.played': '',
    'edx.video.stopped': '',
    'edx.video.paused': '',
    'edx.video.position.changed': '',

    # Course navigation events
    'edx.ui.lms.sequence.outline.selected': '',
    'edx.ui.lms.sequence.next_selected': '',
    'edx.ui.lms.sequence.previous_selected.': '',
    'edx.ui.lms.sequence.tab_selected': '',
    'edx.ui.lms.link_clicked': '',
}
