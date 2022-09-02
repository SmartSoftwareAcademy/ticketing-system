from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # import this

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.signup, name="register"),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/reset_done.html'), name='reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/reset_confirm.html"), name='reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/reset_complete.html'), name='reset_complete'),
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/change_password.html',
            success_url='/'
        ),
        name='change_password'
    ),
]
