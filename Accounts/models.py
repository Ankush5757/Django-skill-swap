from django.db import models
from django.contrib.auth.hashers import make_password

class Student(models.Model):
    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=10, unique=True, default=0000000000)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)  # Token for password reset

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class Profile_Pic(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="profile_picture")
    image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name}'s Profile Picture"
