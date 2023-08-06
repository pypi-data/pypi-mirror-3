"""
sentry.plugins.bases.tag
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from sentry import app
from sentry.filters import Filter
from sentry.models import Event, FilterValue, MessageFilterValue
from sentry.plugins import Plugin
from django.db.models import Sum


def create_tag_filter(plugin):
    class TagFilter(Filter):
        label = plugin.tag_label
        column = plugin.tag

        def get_query_set(self, queryset):
            col, val = self.get_column(), self.get_value()
            if queryset.model == Event:
                queryset = queryset.filter(**dict(
                    group__messagefiltervalue__key=col,
                    group__messagefiltervalue__value=val,
                ))
            else:
                queryset = queryset.filter(**dict(
                    messagefiltervalue__key=col,
                    messagefiltervalue__value=val,
                ))
            return queryset.distinct()

    TagFilter.__name__ = plugin.tag.title() + 'TagFilter'

    return TagFilter


class TagPlugin(Plugin):
    tag = None
    tag_label = None
    index_template = 'sentry/plugins/bases/tag/index.html'
    widget_template = 'sentry/plugins/bases/tag/widget.html'

    def get_tag_values(self, event):
        """
        Must return a list of values.

        >>> get_tag_pairs(event)
        [tag1, tag2, tag3]
        """
        raise NotImplementedError

    def get_unique_tags(self, group):
        return group.messagefiltervalue_set.filter(
            key=self.tag,
        ).values_list(
            'value',
        ).annotate(
            times_seen=Sum('times_seen'),
        ).values_list(
            'value',
            'times_seen',
            'first_seen',
            'last_seen',
        ).order_by('-times_seen')

    def panels(self, request, group, panel_list, **kwargs):
        panel_list.append((self.get_title(), self.get_url(group)))
        return panel_list

    def view(self, request, group, **kwargs):
        return self.render(self.index_template, {
            'title': self.get_title(),
            'tag_label': self.tag_label,
            'tag_name': self.tag,
            'unique_tags': self.get_unique_tags(group),
            'group': group,
        })

    def widget(self, request, group, **kwargs):
        return self.render(self.widget_template, {
            'title': self.get_title(),
            'tag_label': self.tag_label,
            'tag_name': self.tag,
            'unique_tags': list(self.get_unique_tags(group)[:10]),
            'group': group,
        })

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        for value in self.get_tag_values(event):
            FilterValue.objects.get_or_create(
                project=group.project,
                key=self.tag,
                value=value,
            )

            app.buffer.incr(MessageFilterValue, {
                'times_seen': 1,
            }, {
                'group': group,
                'project': group.project,
                'key': self.tag,
                'value': value,
            }, {
                'last_seen': group.last_seen,
            })

    def get_filters(self, project=None, **kwargs):
        if not hasattr(type(self), '_filter_class'):
            self._filter_class = create_tag_filter(self)
        return [self._filter_class]
