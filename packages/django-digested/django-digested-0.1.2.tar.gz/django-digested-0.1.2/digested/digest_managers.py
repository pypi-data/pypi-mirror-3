"""
Foundation for custom digest options at a site.

You should subclass BaseDigestManager and override its methods to
customize most features.
"""

from collections import defaultdict

from django.contrib.contenttypes.models import ContentType

from digested.models import DigestPreference
from digested.models import PREFERENCE_INSTANT
from digested.models import PREFERENCE_WEEKLY


class BaseDigestManager(object):
    """
    Manage the options for a digested item.
    """

    default_preference = PREFERENCE_WEEKLY

    def get_default_preference(self, item):
        """
        Return the default preference for the given item, to be used
        when a user has not set their preference.

        Default implementation returns default_preference, ignoring the
        item passed in.
        """
        return self.default_preference

    def get_items(self):
        """
        Return a set of items which may have updates. Override this.
        """
        return []

    def get_subscribers_for_item(self, item):
        """
        Return the subscribers that are interested in the given
        item. Override this.

        Not all of these need to have a preference set.
        """
        return []

    def get_updates_for_digest(self, item, preference):
        """
        Return a list of updates for the given digest (item/preference
        pair). Override this.
        """
        return []

    def get_preference_for_subscription(self, subscriber, item):
        """
        For a given subscriber/item pair, return the preference that the
        user has set, or the default if no preference was set.
        """
        content_type = ContentType.objects.get_for_model(item)
        try:
            pref_obj = DigestPreference.objects.get(
                user=subscriber,
                object_id=item.id,
                content_type=content_type)
            return pref_obj.preference
        except DigestPreference.DoesNotExist:
            return self.get_default_preference(item)

    def filter_subscribers_by_digest(self, subscribers, item, preference):
        """
        Given a set of subscribers and a digest (item/preference pair),
        return the set of subscribers that should receive this digest.
        """
        for subscriber in subscribers:
            wanted_pref = self.get_preference_for_subscription(subscriber,
                                                               item)
            if wanted_pref == preference:
                yield subscriber

    def get_subscribers_by_digest(self, item, preference):
        """
        Given a digest, return the set of subscribers that should
        receive this digest.
        """
        all_subscribers = self.get_subscribers_for_item(item)
        return self.filter_subscribers_by_digest(
            all_subscribers, item, preference)

    def send_instant_update(self, item, update):
        """
        Send out an instant update for a given item.

        Default implementation calls send_one_instant_update for each
        subscriber that should receive this update.

        You should call this as soon as an update becomes available.
        """
        # TODO: What about an update that fits into multiple
        # items/categories? We don't want the subscriber to receive
        # multiple notifications.
        preference = PREFERENCE_INSTANT
        subscribers = self.get_subscribers_by_digest(item, preference)
        for subscriber in subscribers:
            self.send_one_instant_update(subscriber, update)

    def send_one_instant_update(self, subscriber, update):
        """
        Given a subscriber and an update, send the subscriber an instant
        update. Override this.
        """
        return

    def send_digest_updates(self, preference):
        """
        Send out the digests for a given preference.

        You should call this once per day/week/...

        Default implementation calls send_one_digest_update for each
        subscriber with the set of updates that subscriber should
        receive in this digest.
        """
        updates_by_subscriber = defaultdict(list)
        for item in self.get_items():
            subscribers = self.get_subscribers_by_digest(item, preference)
            updates = self.get_updates_for_digest(item, preference)
            for subscriber in subscribers:
                updates_by_subscriber[subscriber] += updates
        for subscriber, updates in updates_by_subscriber.items():
            self.send_one_digest_update(subscriber, preference, updates)

    def send_one_digest_update(self, subscriber, preference, updates):
        """
        Given a subscriber, preference and a set of updates that the
        user should receive, send the subscriber a digest containing
        these updates. Override this.
        """
        return
