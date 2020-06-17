"""
Filter configured through admin panel. Filters out the events that
do not need to be routed
"""


class RoutingFilter:
    """
    Filter the events using regex. Can be configured through Admin panel.
    """

    def __call__(self, event, **kwargs):
        """
        TODO:
        Add regex based filtering of events. These regex(s) can be
        added and configured through admin panel
        """
        return event
