# from django.urls import path
# from .views import signupview, loginview,logoutview,VerifyResetOTPView,ForgotPasswordView

# urlpatterns = [
#     path('signup/', signupview.as_view(), name="signup"),   
#     path('', loginview.as_view(), name="login"),
#     path('logout/', logoutview.as_view(), name="logout"),
#     path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
#     path('verify-reset-otp/', VerifyResetOTPView.as_view(), name='verify_reset_otp'),
  
# ]
from django.urls import path
from .views import signupview, loginview, logoutview, VerifyResetOTPView, ForgotPasswordView

urlpatterns = [
    path('signup/', signupview.as_view(), name="signup"),   
    path('login/', loginview.as_view(), name="login"),   #  moved login here
    path('logout/', logoutview.as_view(), name="logout"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-reset-otp/', VerifyResetOTPView.as_view(), name='verify_reset_otp'),
]