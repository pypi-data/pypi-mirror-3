from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.core.urlresolvers import reverse, NoReverseMatch
import datetime


class SiteSettingManager(models.Manager):
    def get_current(self):
        site = Site.objects.get_current()
        try:
            return site.pagehelp_settings
        except SiteSetting.DoesNotExist:
            return SiteSetting(site=site)


class SiteSetting(models.Model):
    PERMISSIONS = (
        (0, 'Super-users only'),
        (1, 'Staff members'),
        #(2, 'Any registered user'),
    )
    site = models.OneToOneField(Site, related_name='pagehelp_settings')
    display = models.BooleanField(default=True)
    edit_rights = models.PositiveSmallIntegerField('Create/edit rights',
        choices=PERMISSIONS, default=1)
    delete_rights = models.PositiveSmallIntegerField(choices=PERMISSIONS,
        default=0)

    objects = SiteSettingManager()

    def _has_permission(self, user, level):
        if level == 2:
            return user.is_authenticated()
        if level == 1:
            return user.is_staff
        return user.is_superuser

    def can_edit(self, user):
        return self._has_permission(user, self.edit_rights)

    def can_delete(self, user):
        return self._has_permission(user, self.delete_rights)


class Page(models.Model):
    site = models.ForeignKey(Site)
    url = models.CharField(max_length=255, db_index=True,
           help_text='Either a full URL or a named URL Django pattern.')
    text = models.TextField()
    date_created = models.DateTimeField(default=datetime.datetime.now,
                                        editable=False)
    date_edited = models.DateTimeField(editable=False)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        unique_together = (('site', 'url'),)

    def __unicode__(self):
        return self.url

    def save(self, *args, **kwargs):
        self.date_edited = datetime.datetime.now()
        return super(Page, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if '/' in self.url:
            return self.url
        try:
            return reverse(self.url)
        except NoReverseMatch:
            return ''


class UserDefault(models.Model):
    """
    A per-user override of the default display/hide setting for pages on a
    site.

    """
    site = models.OneToOneField(Site, related_name='pagehelp_user_defaults')
    user = models.ForeignKey('auth.User')
    display = models.BooleanField()


class UserPage(models.Model):
    """
    A per-user override of an individual page's display/hide setting.

    """
    user = models.ForeignKey('auth.User')
    page = models.ForeignKey(Page, related_name='user_pages')
    display = models.BooleanField()
