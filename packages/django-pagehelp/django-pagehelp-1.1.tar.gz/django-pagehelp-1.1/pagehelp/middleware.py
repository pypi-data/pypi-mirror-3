from django.contrib.auth import models as auth_models
from django.core.context_processors import csrf
from django.utils.cache import patch_vary_headers
from django.template.loader import render_to_string
from pagehelp import models, utils
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.encoding import smart_str
import re

KEY = '_pagehelp_anonymous'
RE_APPEND = re.compile('(</body\w*>)', re.IGNORECASE)
RE_PREPEND = re.compile('(</head\w*>)', re.IGNORECASE)
RE_JQUERY = re.compile('<script [^>]*jquery')


class PageMiddleware(object):
    """
    Middleware which adds the contextual help for this page to the response.

    Additionally, when an anonymous user is logged in, any page display
    settings in the cookie are linked with the user.
    """

    def process_request(self, request):
        if not request.user.is_authenticated():
            setattr(request, KEY, True)

    def process_response(self, request, response):
        user = hasattr(request, 'session') and request.user
        if getattr(request, KEY, None):
            if isinstance(user, auth_models.User):
                default, pages = utils.decode_cookie(request)
                # Set the default display.
                utils.set_user_display(request, default, models.UserDefault)
                # Set the display for each page.
                for page_id, display in pages.items():
                    try:
                        page = models.Page.on_site.get(pk=page_id)
                    except models.Page.DoesNotExist:
                        continue
                    utils.set_user_display(request, display, models.UserPage,
                                           page=page)
                utils.encode_cookie(request, response, default, pages)
        if user and user.is_authenticated():
            site_setting = models.SiteSetting.objects.get_current()
            can_edit = site_setting.can_edit(user)
            can_delete = site_setting.can_delete(user)
        else:
            can_edit = can_delete = False
        page = utils.get_page(request.path_info)
        if page or can_edit:
            static_url = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)
            data = {
                'page': page,
                'STATIC_URL': static_url,
                'can_edit': can_edit,
                'can_delete': can_delete,
                'default_open': utils.get_default_display(request),
                'needs_jquery': not RE_JQUERY.search(response.content),
            }
            data.update(csrf(request))
            if page:
                data['next'] = request.get_full_path()
                data['open'] = utils.is_visible(request, page)
            else:
                data['path'] = request.path
                data['site_id'] = Site.objects.get_current().pk
            code = render_to_string('pagehelp.html', data)
            response.content, n = RE_APPEND.subn(smart_str(r'%s\1' % code),
                response.content, count=1)
            if n:
                css = render_to_string('pagehelp_css.html', data)
                response.content = RE_PREPEND.subn(smart_str(r'%s\1' % css),
                                                response.content, count=1)[0]
                # Output may vary depending on the cookie, so set the Vary
                # header.
                patch_vary_headers(response, ('Cookie',))

                # Since the content has been modified, any Etag will now be
                # incorrect.  We could recalculate, but only if we assume that
                # the Etag was set by CommonMiddleware. The safest thing is
                # just to delete. See bug #9163
                del response['ETag']
        return response
