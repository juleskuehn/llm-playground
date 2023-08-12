"""
Override magiclink package methods to only allow PHAC email
"""

from magiclink.views import Login

import logging
import requests
import json

from django.contrib.auth import get_user_model, logout
from django.http import HttpResponseRedirect

from magiclink import settings
from magiclink.forms import LoginForm
from magiclink.helpers import create_magiclink, get_or_create_user
from magiclink.models import MagicLinkError
from magiclink.utils import get_url_path

from llmchat.settings import (
    GC_NOTIFY_API_KEY,
    GC_NOTIFY_TEMPLATE_ID,
    POWER_AUTOMATE_URL,
)

from notifications_python_client.notifications import NotificationsAPIClient

notifications_client = NotificationsAPIClient(
    GC_NOTIFY_API_KEY,
    base_url="https://api.notification.canada.ca"
)

User = get_user_model()
log = logging.getLogger(__name__)


class PhacOnlyLoginView(Login):
    template_name = "auth/login.jinja"

    def post(self, request, *args, **kwargs):
        logout(request)
        context = self.get_context_data(**kwargs)
        context["require_signup"] = settings.REQUIRE_SIGNUP
        form = LoginForm(request.POST)
        if not form.is_valid():
            context["login_form"] = form
            return self.render_to_response(context)

        email = form.cleaned_data["email"]
        if not email.endswith("@phac-aspc.gc.ca"):
            form.add_error("email", "Email must end in @phac-aspc.gc.ca")
            context["login_form"] = form
            return self.render_to_response(context)

        if not settings.REQUIRE_SIGNUP:
            get_or_create_user(email)

        redirect_url = self.login_redirect_url(request.GET.get("next", ""))
        try:
            magiclink = create_magiclink(email, request, redirect_url=redirect_url)
        except MagicLinkError as e:
            form.add_error("email", str(e))
            context["login_form"] = form
            return self.render_to_response(context)

        magiclink_url = magiclink.generate_url(request)

        # Option 1: Use Django SMTP to send email (e.g. through SendGrid)
        # magiclink.send(request)

        # Option 2: Use GC Notify to send email
        # response = notifications_client.send_email_notification(
        #     email_address=email,
        #     template_id=GC_NOTIFY_TEMPLATE_ID,
        #     personalisation={
        #         'magiclink': magiclink_url,
        #         'magiclink_expiry': magiclink.expiry.strftime('%Y-%m-%d %H:%M:%S')
        #     }
        # )

        # Option 3: Send POST request to Power Automate to send email
        url = POWER_AUTOMATE_URL
        payload = json.dumps(
            {
                "email": email,
                "magiclink": magiclink_url,
                "expiry": magiclink.expiry.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)

        log.info(f"Email sent to {email} with link {magiclink_url}.")
        sent_url = get_url_path(settings.LOGIN_SENT_REDIRECT)
        response = HttpResponseRedirect(sent_url)
        if settings.REQUIRE_SAME_BROWSER:
            cookie_name = f"magiclink{magiclink.pk}"
            response.set_cookie(cookie_name, magiclink.cookie_value)
            log.info(f"Cookie {cookie_name} set for {email}")
        return response
