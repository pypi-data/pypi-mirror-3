try:
    from django.contrib.admin.filterspecs import ChoicesFilterSpec as CFilter
    USING_FILTERSPEC = True
except ImportError:
    # In recent versions of Django, FilterSpec is no longer in use.
    from django.contrib.admin.filters import ChoicesFieldListFilter as CFilter
    USING_FILTERSPEC = False

from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django_monitor.conf import STATUS_DICT

class MonitorFilter(CFilter):

    """A custom list-filter to enable filtering by monitor-status."""

    def __init__(
        self, field, request, params, model, model_admin, field_path = None
    ):
        """Extended to set lookup_kwarg & lookup_val."""
        self.lookup_kwarg = 'status'
        # usually, lookup_vals are extracted from request.GET. But we have
        # intentionally removed ``status`` from GET before.
        # (Have a look at ``django_monitor.admin.MonitorAdmin.queryset`` to
        # know why). So we'll apply regex over the url:
        import re
        status_matches = re.findall(
            r'status=(?P<status>%s)' % '|'.join(STATUS_DICT.keys()),
            request.get_full_path()
        )
        self.lookup_val = status_matches[0] if status_matches else None
        self.lookup_choices = STATUS_DICT.keys()
        super(CFilter, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        if not USING_FILTERSPEC:
            # Django >= 1.4 expects title as an attribute, not a method.
            self.title = _("Moderation status")

    def expected_parameters(self):
        """Return the list of expected parameters."""
        return [self.lookup_kwarg]
        
    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }
        for val in self.lookup_choices:
            yield {
                'selected': smart_unicode(val) == self.lookup_val,
                'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                'display': STATUS_DICT[val]
            }

if USING_FILTERSPEC:
    # The older FilterSpec classes require title as a method.
    def title(self):
        """The title displayed above the filter. Only for django < 1.4."""
        return _("Moderation status")
    MonitorFilter.title = title

