
from django.shortcuts import render,redirect
from .serializers import SignupSerializer
from .models import Signup
# import random
# from django.core.mail import send_mail
from django.conf import settings
# from .models import OTP
from django.db .models import Q
def signupview(request):
    message = ""
    error = {}

    if request.method == "POST":
        serializer = SignupSerializer(data=request.POST)

        if serializer.is_valid():
            serializer.save()
            message = "Account created successfully!"
        else:
            error = serializer.errors

    return render(request, "signup.html", {
        "message": message,
        "error": error
    })

def loginview(request):
    message=""
    error={}
    
    if request.method =="POST":
        username_or_email=request.POST.get("username_or_email" )
        password=request.POST.get("password")
        
        try:
            user=Signup.objects.get (Q(username= username_or_email)| Q(email=username_or_email))
            
            if user.password==password:
                request.session['username'] = user.username
                
                return redirect('dashboard')  
            else:
                message = "incorrect password"
                
        except Signup.DoesNotExist:
            error = "user does not exist"
            
    return render(request ,"login.html",{
        "message":message,
        "error":error
    })
            


def dashboardview(request):
    username = request.session.get('username')

    if not username:
        return redirect('login')   

    return render(request, "dashboard.html", {   
        "username": username
    })

        
def logoutview(request):
    request.session.flush()
    return redirect('login')




# def otp_login_view(request):
#     error = ""

#     if request.method == "POST":
#         email = request.POST.get("email")

#         try:
#             user = Signup.objects.get(email=email)

#             otp_code = str(random.randint(100000, 999999))

           
#             OTP.objects.create(user=user, code=otp_code)

#             send_mail(
#                 "Your OTP Code",
#                 f"Your OTP is {otp_code}",
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 fail_silently=False,
#             )

#             request.session['otp_email'] = email
#             return redirect('verify_otp')

#         except Signup.DoesNotExist:
#             error = "Email not registered"

#     return render(request, "otp_login.html", {"error": error})


# def verify_otp_view(request):
#     error = ""

#     email = request.session.get('otp_email')

#     if not email:
#         return redirect('otp_login')

#     if request.method == "POST":
#         entered_otp = request.POST.get("otp")

#         try:
#             user = Signup.objects.get(email=email)

#             # Get latest OTP for this user
#             otp_record = OTP.objects.filter(user=user).last()

#             if otp_record and otp_record.code == entered_otp:
#                 request.session['username'] = user.username
#                 return redirect('dashboard')
#             else:
#                 error = "Invalid OTP"

#         except Signup.DoesNotExist:
#             error = "Something went wrong"

#     return render(request, "verify_otp.html", {"error": error})
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
def forgot_password_view(request):
    error = ""

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = Signup.objects.get(email=email)

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

        except Signup.DoesNotExist:
            error = "Email not registered"

    return render(request, "forgot_password.html", {"error": error})
def verify_reset_otp_view(request):
    error = ""

    email = request.session.get('reset_email')

    if not email:
        return redirect('forgot_password')

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")

        try:
            user = Signup.objects.get(email=email)
            otp_record = OTP.objects.filter(user=user).last()

            if otp_record and otp_record.code == entered_otp:
                user.password = new_password
                user.save()
                return redirect('login')
            else:
                error = "Invalid OTP"

        except Signup.DoesNotExist:
            error = "Something went wrong"

    return render(request, "verify_reset_otp.html", {"error": error})
