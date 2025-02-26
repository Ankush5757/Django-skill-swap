from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Profile_Pic
from django.http import HttpResponse
from django.urls import reverse
import random, string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from Core.models import Skill, UserSkill

def register_view(request):
    messages.get_messages(request).used = True  # Clears old messages

    if request.method == "POST":
        name = request.POST.get('name').strip()
        phone = request.POST.get('phone').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()
        confirm_password = request.POST.get('confirm_password').strip()

        # Validation
        if not all([name, phone, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return redirect(reverse('register'))

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse('register'))

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Enter a valid 10-digit phone number.")
            return redirect(reverse('register'))

        # Check for duplicates
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect(reverse('register'))

        if Student.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered.")
            return redirect(reverse('register'))

        # Create and save the Student
        student = Student(name=name, phone=phone, email=email)
        student.set_password(password)
        student.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect(reverse('login'))

    return render(request, 'register.html')

# .................................................................................................................................................

def login_view(request):
    storage = messages.get_messages(request)
    storage.used = True  # Clears old messages

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([email, password]):
            messages.error(request, "All fields are required.")
            return redirect(reverse('login'))

        try:
            student = Student.objects.get(email=email)
            if student.check_password(password):
                first_name = student.name.split()[0] if student.name else "User"

                # Clear previous session and store new session data
                request.session.flush()
                request.session['student_id'] = student.id
                request.session['student_name'] = first_name
                request.session['student_email'] = student.email

                print("Stored Name in Session:", request.session['student_name'])

                messages.success(request, f"Welcome, {first_name}!")
                return redirect(reverse('home'))
            else:
                messages.error(request, "Invalid password.")
        except Student.DoesNotExist:
            messages.error(request, "Email not found. Please check your credentials.")

        return redirect('login')

    return render(request, 'login.html')



# .................................................................................................................................................

def logout_view(request):
    request.session.flush()  # Clears session completely
    messages.success(request, "You have been logged out successfully.")  
    return redirect(reverse('login'))

# .................................................................................................................................................

def profile_view(request):
    user_id = request.session.get("student_id")
    user = get_object_or_404(Student, id=user_id)
    profile_pic = Profile_Pic.objects.filter(student=user).first()

    # Extract first name safely
    first_name = user.name.split()[0] if user.name else ""

    # Fetch user's skills based on type
    teach_skills = UserSkill.objects.filter(student=user, skill_type="teach")
    learn_skills = UserSkill.objects.filter(student=user, skill_type="learn")
    volunteer_skills = UserSkill.objects.filter(student=user, skill_type="volunteer")

    context = {
        "user": user,
        "profile_pic": profile_pic,
        "first_name": first_name,  # Ensuring first name is available
        "teach_skills": teach_skills,
        "learn_skills": learn_skills,
        "volunteer_skills": volunteer_skills
    }
    return render(request, "profile.html", context)

# .................................................................................................................................................

def upload_profile_pic(request):
    if request.method == "POST" and request.FILES.get("profile_pic"):
        user_id = request.session.get("student_id")  # Fixed session key
        user = get_object_or_404(Student, id=user_id)

        # Check if profile picture already exists
        profile_pic, created = Profile_Pic.objects.get_or_create(student=user)

        # Delete old profile picture to avoid duplicates
        if profile_pic.image:
            profile_pic.image.delete()

        # Save new image
        profile_pic.image = request.FILES["profile_pic"]
        profile_pic.save()

        messages.success(request, "Profile picture updated successfully!")
        return redirect(reverse("profile"))

    messages.error(request, "Failed to upload profile picture.")
    return redirect(reverse("profile"))

# .................................................................................................................................................



def delete_profile_pic(request):
    user_id = request.session.get("student_id")  # Fixed session key
    user = get_object_or_404(Student, id=user_id)

    profile_pic = Profile_Pic.objects.filter(student=user).first()
    if profile_pic:
        if profile_pic.image:
            profile_pic.image.delete()  # Deletes the file from media storage
        profile_pic.delete()  # Deletes the database record
        messages.success(request, "Profile picture deleted successfully!")
    else:
        messages.error(request, "No profile picture found to delete.")

    return redirect(reverse("profile"))

# .................................................................................................................................................


def update_profile(request):
    # Get the logged-in user ID from the session
    user_id = request.session.get("student_id")
    
    if not user_id:
        messages.error(request, "You need to log in first.")
        return redirect("login")

    # Get the Student instance
    student = get_object_or_404(Student, id=user_id)

    if request.method == "POST":
        student.name = request.POST.get("name", student.name)
        student.email = request.POST.get("email", student.email)
        student.phone = request.POST.get("phone", student.phone)
        student.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "update_profile.html", {"student": student})

# .............................................................................................................................................

def delete_account(request):
    user_id = request.session.get("student_id")

    if not user_id:
        messages.error(request, "You need to log in first.")
        return redirect("login")

    # Get the Student instance
    student = get_object_or_404(Student, id=user_id)

    # Delete profile picture if exists
    profile_pic = Profile_Pic.objects.filter(student=student).first()
    if profile_pic and profile_pic.image:
        profile_pic.image.delete()  # Deletes the file from media storage
        profile_pic.delete()

    # Delete the student record
    student.delete()

    # Clear session
    request.session.flush()

    messages.success(request, "Your account has been deleted successfully.")
    return redirect("home")  # Redirect to home page


# ...............................................................................................................................................

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, "Email is required.")
            return redirect('forgot_password')

        try:
            student = Student.objects.get(email=email)

            # Generate a secure reset token
            reset_token = get_random_string(length=32)
            student.reset_token = reset_token
            student.save()

            reset_link = request.build_absolute_uri(reverse('reset_password', args=[reset_token]))

            # Send email
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "A password reset link has been sent to your email.")
        except Student.DoesNotExist:
            messages.error(request, "No account found with this email.")

        return redirect('forgot_password')

    return render(request, 'forgot_password.html')
# ...............................................................................................................................................

def reset_password_view(request, reset_token):
    try:
        student = Student.objects.get(reset_token=reset_token)
    except Student.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    if request.method == "POST":
        new_password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect(reverse('reset_password', args=[reset_token]))

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse('reset_password', args=[reset_token]))

        # Hash password before saving
        student.password = make_password(new_password)
        student.reset_token = None  # Clear the reset token after use
        student.save()

        messages.success(request, "Password reset successful. You can now log in.")
        return redirect('login')

    return render(request, 'reset_password.html', {'reset_token': reset_token})


# ........................................................................................................................................



def contact(request):
    return render(request,'contact.html')