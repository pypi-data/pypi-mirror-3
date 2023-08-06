from datetime import date, timedelta

from django.core.urlresolvers import reverse
from admin_tools.dashboard.modules import DashboardModule, AppList

from daycare.models import MissingURL, Redirect, URLHit


class DayCareStatusModule(DashboardModule):

    def __init__(self, **kwargs):
        super(DayCareStatusModule, self).__init__(**kwargs)
        self.title = kwargs.get('title', 'Daycare status')
        self.template = "daycare/dashboard_status_module.html"
        self.deletable = False
        self.apps = kwargs.get('apps', None)
        self.icons_dir = kwargs.get('icons_dir', '/static/admin_custom/icons/')

    def is_empty(self):
        return False

    def init_with_context(self, context):
        # apps links
        for m in self.apps:
            # if type(m[0]) == ModelBase:
            if context.get("request").user.has_module_perms(m[0]._meta.app_label):
                m[0].admin_url = reverse('admin:%s_%s_changelist' %
                                         (m[0]._meta.app_label, m[0].__name__.lower()))

        month_ago = date.today() - timedelta(days=30)
        week_ago = date.today() - timedelta(days=7)

        self.redirects = Redirect.objects.all().count()
        self.draft_redirects = Redirect.objects.filter(status=Redirect.STATUS_DRAFT).count()
        self.urls_without_redirects = len(
                                          filter(
                                                 lambda url: Redirect.objects.filter(catch_url=url.url).count(),
                                                 MissingURL.objects.all()
                                                )
                                          )
        self.urlhits_last_week = URLHit.objects.filter(date__range=(date.today(), week_ago)).count()
        self.urlhits_last_month = URLHit.objects.filter(date__range=(date.today(), month_ago)).count()

        return super(DayCareStatusModule, self).init_with_context(context)
