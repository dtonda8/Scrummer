from django.urls import path
from accounts.forms import UserAuthForm
from django.contrib.auth import views as auth_views
from django.urls import path
from accounts.views import ResetPasswordView, team_stats

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=UserAuthForm,
            next_page="/"),
        name='login'
        ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name="accounts/logout.html",
            next_page=None)
        ),
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
    path('team-statistics/', team_stats, name='team_statistics'),
]
