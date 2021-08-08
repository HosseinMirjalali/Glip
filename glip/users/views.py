import environ
import requests
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return self.request.user.get_absolute_url()  # type: ignore [union-attr]

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()

"""Automatic token refresh"""

env = environ.Env()


def get_new_access_from_refresh(request):
    """On-demand function that updates the user's access token"""

    client_id = SocialApp.objects.get(provider__iexact="twitch").client_id
    client_secret = SocialApp.objects.get(provider__iexact="twitch").secret
    account = SocialAccount.objects.get(user=request.user)
    st = SocialToken.objects.get(account=account)
    rt = SocialToken.objects.get(account=account).token_secret
    refresh_token_url2 = f"https://id.twitch.tv/oauth2/token?grant_type=refresh_token&refresh_token={rt}&client_id={client_id}&client_secret={client_secret}"  # # noqa: E501
    response = requests.post(refresh_token_url2)
    data = response.json()
    new_token = data["access_token"]
    new_refresh = data["refresh_token"]
    st.token = new_token
    st.token_secret = new_refresh
    st.save()
    return data
