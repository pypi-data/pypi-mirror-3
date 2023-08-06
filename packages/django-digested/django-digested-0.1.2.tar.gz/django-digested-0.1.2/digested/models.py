"""
Models for django-digest. We just add a model to remember a user's
digest preferences.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

PREFERENCE_INSTANT = 'I'
PREFERENCE_DAILY = 'D'
PREFERENCE_WEEKLY = 'W'
PREFERENCES=((PREFERENCE_INSTANT, 'Instant'),
             (PREFERENCE_DAILY, 'Daily'),
             (PREFERENCE_WEEKLY, 'Weekly'))

class DigestPreference(models.Model):
    """
    The digest preference that a given user has selected for an item.
    """
    # Fields for the generic key.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    # The actual, useful fields.
    item = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, related_name='digest_preferences')
    preference = models.CharField(max_length=1, choices=PREFERENCES)

    def __unicode__(self):
        return u'%s wants %s updates for %s' % (
            self.user, self.get_preference_display().lower(), self.item)
