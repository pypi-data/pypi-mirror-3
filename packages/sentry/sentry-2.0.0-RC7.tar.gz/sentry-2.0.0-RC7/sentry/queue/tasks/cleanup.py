"""
sentry.queue.tasks.cleanup
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""


def cleanup(days=30, logger=None, site=None, server=None, level=None,
            project=None):
    """
    Deletes a portion of the trailing data in Sentry based on
    their creation dates. For example, if ``days`` is 30, this
    would attempt to clean up all data thats older than 30 days.

    :param logger: limit all deletion scopes to messages from the
                   specified logger.
    :param site: limit the message deletion scope to the specified
                 site.
    :param server: limit the message deletion scope to the specified
                   server.
    :param level: limit all deleteion scopes to messages that are greater
                  than or equal to level.
    """
    import datetime

    from sentry.models import Group, Event, MessageCountByMinute, \
                              MessageFilterValue, FilterValue
    from sentry.utils.query import RangeQuerySetWrapper, SkinnyQuerySet

    # TODO: we should collect which messages above were deleted
    # and potentially just send out post_delete signals where
    # GroupedMessage can update itself accordingly
    ts = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    # Message
    qs = SkinnyQuerySet(Event).filter(datetime__lte=ts)
    if logger:
        qs = qs.filter(logger=logger)
    if site:
        qs = qs.filter(site=site)
    if server:
        qs = qs.filter(server_name=server)
    if level:
        qs = qs.filter(level__gte=level)
    if project:
        qs = qs.filter(project=project)

    groups_to_check = set()
    for obj in RangeQuerySetWrapper(qs):
        print ">>> Removing <%s: id=%s>" % (obj.__class__.__name__, obj.pk)
        obj.delete()
        groups_to_check.add(obj.group_id)

    if not (server or site):
        # MessageCountByMinute
        qs = SkinnyQuerySet(MessageCountByMinute).filter(date__lte=ts)
        if logger:
            qs = qs.filter(group__logger=logger)
        if level:
            qs = qs.filter(group__level__gte=level)
        if project:
            qs = qs.filter(project=project)

        for obj in RangeQuerySetWrapper(qs):
            print ">>> Removing <%s: id=%s>" % (obj.__class__.__name__, obj.pk)
            obj.delete()

        # GroupedMessage
        qs = SkinnyQuerySet(Group).filter(last_seen__lte=ts)
        if logger:
            qs = qs.filter(logger=logger)
        if level:
            qs = qs.filter(level__gte=level)
        if project:
            qs = qs.filter(project=project)

        for obj in RangeQuerySetWrapper(qs):
            for key, value in SkinnyQuerySet(MessageFilterValue).filter(group=obj).values_list('key', 'value'):
                if not MessageFilterValue.objects.filter(key=key, value=value).exclude(group=obj).exists():
                    print ">>> Removing <FilterValue: key=%s, value=%s>" % (key, value)
                    FilterValue.objects.filter(key=key, value=value).delete()
            print ">>> Removing <%s: id=%s>" % (obj.__class__.__name__, obj.pk)
            obj.delete()

    # attempt to cleanup any groups that may now be empty
    groups_to_delete = []
    for group_id in groups_to_check:
        if not Event.objects.filter(group=group_id).exists():
            groups_to_delete.append(group_id)

    if groups_to_delete:
        for obj in SkinnyQuerySet(Group).filter(pk__in=groups_to_delete):
            for key, value in SkinnyQuerySet(MessageFilterValue).filter(group=obj).values_list('key', 'value'):
                if not MessageFilterValue.objects.filter(key=key, value=value).exclude(group=obj).exists():
                    print ">>> Removing <FilterValue: key=%s, value=%s>" % (key, value)
                    FilterValue.objects.filter(key=key, value=value).delete()
            print ">>> Removing <%s: id=%s>" % (obj.__class__.__name__, obj.pk)
            obj.delete()
