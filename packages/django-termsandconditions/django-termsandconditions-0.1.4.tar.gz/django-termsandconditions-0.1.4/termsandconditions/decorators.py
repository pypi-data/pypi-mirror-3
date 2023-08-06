"""View Decorators for termsandconditions module"""
import urlparse
from functools import wraps
from django.http import HttpResponseRedirect, QueryDict
from django.utils.decorators import available_attrs
from models import TermsAndConditions
from middleware import ACCEPT_TERMS_PATH


def terms_required(view_func):
    """
    This decorator checks to see if the user is logged in, and if so, if they have accepted the site terms.
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        """Method to wrap the view passed in"""
        if not request.user.is_authenticated() or TermsAndConditions.agreed_to_latest(request.user):
            return view_func(request, *args, **kwargs)

        currentPath = request.META['PATH_INFO']
        login_url_parts = list(urlparse.urlparse(ACCEPT_TERMS_PATH))
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring['returnTo'] = currentPath
        login_url_parts[4] = querystring.urlencode(safe='/')
        return HttpResponseRedirect(urlparse.urlunparse(login_url_parts))
    return _wrapped_view