"""Factories needed for unit tests in the app"""

import factory
from eventtracking.django.models import RegExFilter


class RegExFilterFactory(factory.DjangoModelFactory):

    class Meta:
        model = RegExFilter
