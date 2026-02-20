
from django.db import models

class Signup(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150)  # plain password
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
# class OTP(models.Model):
#     user = models.ForeignKey(Signup, on_delete=models.CASCADE)
#     code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.code}"
class OTP(models.Model):
    user = models.ForeignKey(Signup, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
