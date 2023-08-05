from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.cache import cache
from django.utils.http import cookie_date
from pagehelp import models
from django.conf import settings
import datetime
import time

COOKIE_NAME = 'page_display'


def get_default_display(request=None):
    """
    Get the default page display setting.

    If the ``request`` argument is provided, the display setting will first be
    checked specifically for the user.

    If the ``request`` argument was not provided, or the user has not
    overridden the default setting, the default display setting for the current
    site will be calculated (and the result is cached to avoid excessive
    database activity).

    """
    if request:
        if isinstance(request.user, User):
            try:
                return models.UserDefault.objects.get(user=request.user)\
                                                 .display
            except models.UserDefault.DoesNotExist:
                pass
        else:
            return decode_cookie(request)[0]
    site = Site.objects.get_current()
    cache_key = 'pagehelp_display_%s' % site.pk
    display = cache.get(cache_key)
    if display is None:
        site_settings = models.SiteSetting.objects.get_current()
        display = site_settings.display
        cache.set(cache_key, display)
    return display


def set_user_display(request, display, model, **model_kwargs):
    """
    Link a display setting with a user.

    """
    if display is None or not isinstance(request.user, User):
        return

    try:
        obj = model.objects.get(user=request.user, **model_kwargs)
    except model.DoesNotExist:
        obj = None
    if display == get_default_display(request):
        if obj:
            obj.delete()
    else:
        if not obj:
            obj = model(user=request.user, display=display, **model_kwargs)
            obj.site_id = settings.SITE_ID
            obj.save()
        elif obj.display != display:
            obj.display = display
            obj.save()


def _decode_cookie_setting(text):
    return {'0': False, '1': True}.get(text)


def _encode_cookie_setting(setting, default=None, always_encode=False):
    """
    Encode the boolean value for display as a string for use in a cookie.

    An empty string is returned if the display matches the default display
    setting (unless ``always_encode`` is ``True``).

    """
    mapping = {False: '0', True: '1'}
    if not always_encode:
        if default is None:
            default = get_default_display()
        del mapping[default]
    return mapping.get(setting, '')


def decode_cookie(request):
    """
    Decode the cookie containing all the custom display settings for a user,
    returning a 2-part tuple containing the default setting and a dictionary of
    page settings.

    The keys of the page settings dictionary are page ids and the values are
    a boolean for the related display setting.

    """
    text = request.COOKIES.get(COOKIE_NAME, '')
    default = get_default_display()
    pages = {}
    if text and text.startswith(_encode_cookie_setting(default,
                                                       always_encode=True)):
        bits = text[1:].split(',')
        display = _decode_cookie_setting(bits[0])
        if display is not None:
            default = display
        for page in bits[1:]:
            try:
                page_id, setting = page.split('=')
                page_id = int(page_id)
            except (ValueError, TypeError):
                continue
            pages[page_id] = _decode_cookie_setting(setting)
    return default, pages


def encode_cookie(request, response, default=None, pages=None):
    """
    Encode a cookie with a user's display settings.

    Only settings which differ from the default will be saved. If no settings
    differ, any existing cookie will be deleted.

    """
    site_default = get_default_display()
    text = '%s%s' % (_encode_cookie_setting(site_default, always_encode=True),
                     _encode_cookie_setting(default))
    pages = pages or {}
    for page_id, setting in pages.items():
        setting = _encode_cookie_setting(setting, default=default)
        if not setting:
            continue
        if isinstance(page_id, models.Page):
            page_id = page_id.pk
        text = '%s,%s=%s' % (text, page_id, setting)
    if len(text) > 1:
        delta = datetime.timedelta(days=365)
        max_age = max(0, delta.days * 86400 + delta.seconds)
        expires = cookie_date(time.time() + max_age)
        response.set_cookie(COOKIE_NAME, text, max_age=max_age,
                            expires=expires)
    elif COOKIE_NAME in request.COOKIES:
        response.delete_cookie(COOKIE_NAME)


def get_page(path):
    """
    Get a page object relating to the url ``path`` argument, or ``None`` if no
    matching page exists.

    """
    direct_urls = models.Page.on_site.filter(url=path)
    if direct_urls:
        return direct_urls[0]
    resolver = urlresolvers.get_resolver(None)
    try:
        view = resolver.resolve(path)[0]
    except urlresolvers.Resolver404:
        return

    def find_matching_pattern(resolver):
        for pattern in resolver.url_patterns:
            if isinstance(pattern, urlresolvers.RegexURLResolver):
                match = find_matching_pattern(pattern)
                if match:
                    return match
                continue
            if pattern.callback != view or not pattern.name:
                continue
            named_urls = models.Page.on_site.filter(url=pattern.name)
            if named_urls:
                return named_urls[0]

    return find_matching_pattern(resolver)


def is_visible(request, page):
    """
    Return a boolean as to whether the help should be visible for the given
    user.

    """
    if isinstance(request.user, User):
        try:
            return page.user_pages.get(user=request.user).display
        except models.UserPage.DoesNotExist:
            pass
        return get_default_display(request)
    default, pages = decode_cookie(request)
    return pages.get(page.pk, default)
