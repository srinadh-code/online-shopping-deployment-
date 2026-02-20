from django.urls import path
from .views import signupview, loginview,logoutview,verify_reset_otp_view,forgot_password_view

urlpatterns = [
    path('', signupview, name="signup"),   
    path('login/', loginview, name="login"),
    # path('dashboard/', dashboardview, name="dashboard"),
    path('logout/', logoutview, name="logout"),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', verify_reset_otp_view, name='verify_reset_otp'),

    # path('otp-login/', otp_login_view, name='otp_login'),
    # path('verify-otp/', verify_otp_view, name='verify_otp'),
]
