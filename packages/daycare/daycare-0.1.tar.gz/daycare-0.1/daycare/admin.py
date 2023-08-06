from django.contrib import admin

from daycare.models import MissingURL, Redirect, URLHit


class MissingURLAdmin(admin.ModelAdmin):
    model = MissingURL
    list_display = ('url',
                    'hits',
                    'hits_last_month',
                    'hits_last_week',
                    'last_hit',
                    'first_hit',
                    'has_redirect')

    def queryset(self, request):
        # Below code is slowing down but I find it most reliable way
        # to have accurate hits counters set on objects' fields.
        # All in all usually there's not that much 404s so
        # a bit of suboptimal code in admin won't hurt that much.

        # Update field's value to cached (fetched) ones:
        for url in MissingURL.objects.all():
            if url.hits != url.get_hits() \
            or url.hits_last_month != url.get_hits_last_month() \
            or url.hits_last_week != url.get_hits_last_week():
                url.hits = url.get_hits()
                url.hits_last_month = url.get_hits_last_month()
                url.hits_last_week = url.get_hits_last_week()
                url.save()

        return super(MissingURLAdmin, self).queryset(request)


class RedirectAdmin(admin.ModelAdmin):
    model = Redirect
    list_display = ('catch_url', 'redirect_url', 'status',
                    'created', 'modified', 'created_automatically')


admin.site.register(MissingURL, MissingURLAdmin)
admin.site.register(Redirect, RedirectAdmin)
