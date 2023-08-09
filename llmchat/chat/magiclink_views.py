"""
Override magiclink package methods to only allow PHAC email
"""

from magiclink.views import Login

import logging

from django.contrib.auth import get_user_model, logout
from django.http import HttpResponseRedirect

from magiclink import settings
from magiclink.forms import LoginForm
from magiclink.helpers import create_magiclink, get_or_create_user
from magiclink.models import MagicLinkError
from magiclink.utils import get_url_path

User = get_user_model()
log = logging.getLogger(__name__)

class PhacOnlyLoginView(Login):

    template_name = 'login.jinja'

    def post(self, request, *args, **kwargs):
        logout(request)
        context = self.get_context_data(**kwargs)
        context['require_signup'] = settings.REQUIRE_SIGNUP
        form = LoginForm(request.POST)
        if not form.is_valid():
            context['login_form'] = form
            return self.render_to_response(context)

        email = form.cleaned_data['email']
        if not email.endswith('@phac-aspc.gc.ca'):
            form.add_error('email', 'Email must end in @phac-aspc.gc.ca')
            context['login_form'] = form
            return self.render_to_response(context)

        if not settings.REQUIRE_SIGNUP:
            get_or_create_user(email)

        redirect_url = self.login_redirect_url(request.GET.get('next', ''))
        try:
            magiclink = create_magiclink(
                email, request, redirect_url=redirect_url
            )
        except MagicLinkError as e:
            form.add_error('email', str(e))
            context['login_form'] = form
            return self.render_to_response(context)

        magiclink.send(request)

        sent_url = get_url_path(settings.LOGIN_SENT_REDIRECT)
        response = HttpResponseRedirect(sent_url)
        if settings.REQUIRE_SAME_BROWSER:
            cookie_name = f'magiclink{magiclink.pk}'
            response.set_cookie(cookie_name, magiclink.cookie_value)
            log.info(f'Cookie {cookie_name} set for {email}')
        return response
