from django.db.models.signals import pre_save, post_save

from daycare.models import Redirect, PageURLTrack

from cms.models import Page, Title


def page_pre_save_handler(sender, instance, *args, **kwargs):
    """
    Remember page's last absolute url.
    """
    if instance.id:
        pagetrack, created = PageURLTrack.objects.get_or_create(
                                                    page_id=instance.id,
                                                    last_url=instance.get_absolute_url())
        pagetrack.save()


def title_post_save_handler(sender, instance, *args, **kwargs):
    """
    Check if page's absolute url has changed.
    If yes, then make a draft redirect, which user can activate manually.
    """
    page = instance.page
    new_url = page.get_absolute_url()
    for pagetrack in PageURLTrack.objects.filter(page_id=page.id):
        redirects = Redirect.objects.filter(catch_url=pagetrack.last_url,
                                            created_automatically=True)
        if redirects:
            for redirect in redirects:
                redirect.redirect_url = new_url
                redirect.save()
        else:
            #  this PageURLTrack had no redirects (so was created in pre_save() a second ago),
            #  try to make new redirect
            if pagetrack.last_url != new_url:
                Redirect(
                    catch_url=pagetrack.last_url,
                    redirect_url=new_url,
                    status=Redirect.STATUS_DRAFT,
                    created_automatically=True).save()


pre_save.connect(page_pre_save_handler, sender=Page)
post_save.connect(title_post_save_handler, sender=Title)


class CMSPageURLTrackMiddleware:
    """
    Dummy middleware class, used just to cause this module import
    and thus conntect pre_save and post_save signals.
    """
    pass
