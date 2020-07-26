"""
Factories needed for unit tests in the app
"""

import factory
from eventtracking.django.models import RegExFilter


class RegExFilterFactory(factory.DjangoModelFactory):
    """
    Model factory for `RegExFilter`.
    """

    class Meta:
        model = RegExFilter
