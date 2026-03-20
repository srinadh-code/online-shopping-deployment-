
from .models import OTP
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout,login,authenticate
from .serializers import SignupSerializer
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings


class signupview(View):

    def get(self, request):
        return render(request, "signup.html")
   
    def post(self, request):
        serializer = SignupSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, " Account created successfully! Please login.")
            return redirect("login")
        return render(request, "signup.html", {
            "errors": serializer.errors
        })
from django.core.mail import send_mail
from django.conf import settings

class loginview(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username_or_email = request.POST.get("username_or_email")
        password = request.POST.get("password")

        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)

            #  SEND EMAIL AFTER LOGIN
#             subject = "Welcome Back to SRIA NEXT GEN 🛍️"
#             message = f"""
# Hi {user.username},

# Welcome back to SRIA NEXT GEN ONLINE SHOPPPING!

# ✨ "Shopping is not just buying, it's an experience."

# We're excited to have you again.

# 🎁 Special Offer Just for You:
# Get 30% OFF on your first order!

# Start shopping now and grab your favorites.

# Happy Shopping 🛒
# - SRIA Team
# """

#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [user.email],
#                 fail_silently=True,  # avoid crash if email fails
#             )
#             print(user.email)
            

            return redirect("dashboard")

        else:
            return render(request, "login.html", {
                "error": "Invalid username/email or password"
            })

class logoutview(View):
    def get(self, request):
        logout(request)
        return redirect("login")


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, "forgot_password.html")

    def post(self, request):
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)

            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, code=otp_code)

            send_mail(
                "Password Reset OTP",
                f"Your OTP is {otp_code}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['reset_email'] = email
            return redirect('verify_reset_otp')

        except User.DoesNotExist:
            return render(request, "forgot_password.html", {
                "error": "Email not registered"
            })
            
class VerifyResetOTPView(View):
    def get(self, request):
        if not request.session.get('reset_email'):
            return redirect('forgot_password')
        return render(request, "verify_reset_otp.html")

    def post(self, request):
        email = request.session.get('reset_email')

        if not email:
            return redirect('forgot_password')

        entered_otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")

        try:
            user = User.objects.get(email=email)
            otp_record = OTP.objects.filter(user=user).last()

            if otp_record and otp_record.code == entered_otp:
                user.set_password(new_password)   
                user.save()

                return redirect('login')
            else:
                return render(request, "verify_reset_otp.html", {
                    "error": "Invalid OTP"
                })
        except User.DoesNotExist:
            return redirect('forgot_password')