from django import http
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from pagehelp import models, utils


def _next_page(request):
    """
    Return the context.
    """
    next = request.REQUEST.get('next')
    if next and not '//' in next:
        return next


def set_default(request, show):
    """
    Set a user's default display setting.

    """
    next = _next_page(request)
    if not next or request.method != 'POST':
        raise http.Http404

    set_cookie = False
    if isinstance(request.user, User):
        utils.set_user_display(request, show, models.UserDefault,
                               site=Site.objects.get_current())
        page = utils.get_page(next)
        if page:
            if isinstance(request.user, User):
                utils.set_user_display(request, show, models.UserPage,
                                       page=page)
    else:
        set_cookie = True
        default, pages = utils.decode_cookie(request)
        default = show
    response = http.HttpResponseRedirect(next)
    if set_cookie:
        utils.encode_cookie(request, response, default, pages)
    return response


def set_page(request, show):
    """
    Set a user's display setting for an individual page.

    """
    next = _next_page(request)
    if not next or request.method != 'POST':
        raise http.Http404

    page = utils.get_page(next)
    if not page:
        raise http.Http404

    set_cookie = False
    if isinstance(request.user, User):
        utils.set_user_display(request, show, models.UserPage, page=page)
    else:
        set_cookie = True
        default, pages = utils.decode_cookie(request)
        pages[page.pk] = show
    response = http.HttpResponseRedirect(next)
    if set_cookie:
        utils.encode_cookie(request, response, default, pages)
    return response
