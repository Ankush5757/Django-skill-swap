from django.shortcuts import render, redirect, get_object_or_404
from Accounts.models import Student,Profile_Pic
from .models import UserSkill, Skill, SwapRequest
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

#................................................................................................................................................................................

def home(request):
    student_name = None
    profile_pic = None

    if "student_id" in request.session:  
        student_id = request.session.get("student_id")
        student = Student.objects.filter(id=student_id).first()
        
        if student:
            student_name = student.name.split()[0]  # Get the first name
            profile_pic = Profile_Pic.objects.filter(student=student).first()

    context = {"student_name": student_name, "profile_pic": profile_pic}
    return render(request, "home.html", context)

#................................................................................................................................................................................


def aboutus(request):
    return render(request,'aboutus.html')

#................................................................................................................................................................................

def add_skill(request):
    if request.method == "POST":
        student_id = request.session.get("student_id")
        if not student_id:
            return redirect("login")

        student = Student.objects.get(id=student_id)
        skill_type = request.POST.get("skill_type")

        if skill_type == "swap":
            teach_skill_id = request.POST.get("teach_skill")
            learn_skill_id = request.POST.get("learn_skill")

            if not teach_skill_id and not learn_skill_id:
                messages.error(request, "Please select at least one skill to Teach or Learn.")
                return redirect("add_skill")

            if teach_skill_id and learn_skill_id and teach_skill_id == learn_skill_id:
                messages.error(request, "You cannot select the same skill for Teach & Learn.")
                return redirect("add_skill")

            if teach_skill_id:
                teach_skill = Skill.objects.get(id=teach_skill_id)
                if UserSkill.objects.filter(student=student, skill=teach_skill, skill_type="teach").exists():
                    messages.error(request, f"You already have {teach_skill.name} as a teaching skill.")
                else:
                    proficiency = request.POST.get("skill_proficiency", "beginner")
                    UserSkill.objects.create(student=student, skill=teach_skill, skill_type="teach", skill_proficiency=proficiency)

            if learn_skill_id:
                learn_skill = Skill.objects.get(id=learn_skill_id)
                if UserSkill.objects.filter(student=student, skill=learn_skill, skill_type="learn").exists():
                    messages.error(request, f"You already have {learn_skill.name} as a learning skill.")
                else:
                    UserSkill.objects.create(student=student, skill=learn_skill, skill_type="learn")

        elif skill_type == "volunteer":
            volunteer_skill_id = request.POST.get("volunteer_skill")
            if not volunteer_skill_id:
                messages.error(request, "Please select a skill to volunteer.")
                return redirect("add_skill")

            volunteer_skill = Skill.objects.get(id=volunteer_skill_id)
            if UserSkill.objects.filter(student=student, skill=volunteer_skill, skill_type="volunteer").exists():
                messages.error(request, f"You already have {volunteer_skill.name} as a volunteer skill.")
            else:
                proficiency = request.POST.get("skill_proficiency", "beginner")  # ✅ Collect proficiency
                UserSkill.objects.create(student=student, skill=volunteer_skill, skill_type="volunteer", skill_proficiency=proficiency)

        messages.success(request, "Skills added successfully!")
        return redirect("profile")

    all_skills = Skill.objects.all()
    return render(request, "add_skill.html", {"all_skills": all_skills})

#................................................................................................................................................................................

def remove_skill(request, skill_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login")

    student = get_object_or_404(Student, id=student_id)
    skill = get_object_or_404(UserSkill, id=skill_id, student=student)
    skill.delete()

    messages.success(request, "Skill removed successfully.")
    return redirect("profile")

#................................................................................................................................................................................

def find_skills(request):
    user_id = request.session.get("student_id")
    current_user = get_object_or_404(Student, id=user_id)

    # Fetch users who are involved in skill swaps (teaching/learning)
    swap_users = Student.objects.exclude(id=user_id).filter(
        user_skills__skill_type__in=["teach", "learn"]
    ).distinct().prefetch_related("user_skills__skill").select_related("profile_picture")

    # Fetch users who are volunteers only and ensure proficiency is not None
    volunteer_users = Student.objects.exclude(id=user_id).filter(
        user_skills__skill_type="volunteer", user_skills__skill_proficiency__isnull=False
    ).distinct().prefetch_related("user_skills__skill").select_related("profile_picture")

    context = {
        "swap_users": swap_users,
        "volunteer_users": volunteer_users,
    }
    return render(request, "find_skills.html", context)

#................................................................................................................................................................................

def edit_skill(request, skill_id):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    skill = get_object_or_404(UserSkill, id=skill_id, student=student)

    if request.method == "POST":
        if skill.skill_type == "teach":  # ✅ Allow proficiency update ONLY for "teach" type
            skill.skill_proficiency = request.POST.get("skill_proficiency", skill.skill_proficiency)
            skill.save()
            messages.success(request, "Skill proficiency updated successfully!")
        else:
            messages.error(request, "You can only update proficiency for teaching skills.")

        return redirect("profile")

    return render(request, "edit_skill.html", {"skill": skill})


#................................................................................................................................................................................

def delete_skill(request, skill_id):
    student_id = request.session.get("student_id")
    student = get_object_or_404(Student, id=student_id)
    skill = get_object_or_404(UserSkill, id=skill_id, student=student)
    skill.delete()

    messages.success(request, "Skill deleted successfully!")
    return redirect("profile")

#................................................................................................................................................................................

def send_swap_request(request, skill_id):
    user_id = request.session.get("student_id")
    sender = get_object_or_404(Student, id=user_id)
    skill = get_object_or_404(UserSkill, id=skill_id)
    receiver = skill.student  # Get the owner of the skill

    # Ensure sender is not sending a request to themselves
    if sender == receiver:
        messages.error(request, "You cannot send a request to yourself.")
        return redirect("find_skills")

    # Prevent duplicate swap requests
    existing_request = SwapRequest.objects.filter(sender=sender, receiver=receiver, skill=skill).first()
    if existing_request:
        messages.warning(request, "You have already sent a request for this skill.")
        return redirect("find_skills")

    # Create a new skill swap request
    SwapRequest.objects.create(sender=sender, receiver=receiver, skill=skill)

    messages.success(request, "Swap request sent successfully!")
    return redirect("find_skills")

#................................................................................................................................................................................

def swap_requests(request):
    user_id = request.session.get("student_id")

    # Incoming requests (Other users sent requests to you)
    incoming_requests = SwapRequest.objects.filter(receiver_id=user_id)

    # Outgoing requests (Requests you sent to other users)
    outgoing_requests = SwapRequest.objects.filter(sender_id=user_id)

    context = {
        "incoming_requests": incoming_requests,
        "outgoing_requests": outgoing_requests,
    }

    return render(request, "swap_requests.html", context)

#................................................................................................................................................................................

def accept_request(request, request_id):
    swap_request = get_object_or_404(SwapRequest, id=request_id)

    # Ensure only the receiver can accept the request
    if request.session.get("student_id") != swap_request.receiver.id:
        messages.error(request, "Unauthorized action!")
        return redirect("swap_requests")

    swap_request.status = "accepted"
    swap_request.save()

    # Send email notification
    subject = "Skill Swap Request Accepted"
    message = (
        f"Hello {swap_request.sender.name},\n\n"
        f"Great news! Your skill swap request for '{swap_request.skill.skill.name}' has been accepted by {swap_request.receiver.name}.\n\n"
        f"You can now connect and start your skill exchange.\n\n"
        f"Best regards,\n{swap_request.receiver.name}"
    )
    
    recipient_email = swap_request.sender.email  
    send_mail(subject, message, "jadhavankush440@gmail.com", [recipient_email])

    messages.success(request, f"Skill Swap request accepted successfully!")
    return redirect("matching_swaps") 

#................................................................................................................................................................................

@csrf_exempt
def reject_request(request, request_id):
    swap_request = get_object_or_404(SwapRequest, id=request_id)

    # Ensure only the receiver can reject the request
    if request.session.get("student_id") != swap_request.receiver.id:
        messages.error(request, "You are not authorized to reject this request.")
        return redirect("swap_requests")

    swap_request.status = "rejected"
    swap_request.save()

    messages.success(request, f"Swap request for {swap_request.skill.skill} rejected.")
    return redirect("swap_requests")

#................................................................................................................................................................................


def matching_swaps(request):
    user_id = request.session.get("student_id")  

    # Fetch all accepted swap requests where the user is sender or receiver
    matched_swaps = SwapRequest.objects.filter(
        status="accepted"
    ).filter(
        sender_id=user_id
    ) | SwapRequest.objects.filter(
        status="accepted"
    ).filter(
        receiver_id=user_id
    )

    # Store the user's matched partners
    swap_partners = []
    for swap in matched_swaps:
        if swap.sender.id == user_id:
            swap_partners.append(swap.receiver)  # If user is sender, show receiver info
        else:
            swap_partners.append(swap.sender)  # If user is receiver, show sender info

    context = {
        "matched_swaps": matched_swaps,
        "swap_partners": swap_partners,  # List of users the logged-in user matched with
    }
    return render(request, "matching_swaps.html", context)
#................................................................................................................................................................................

def cancel_request(request, request_id):
    swap_request = get_object_or_404(SwapRequest, id=request_id)

    # Ensure only the sender can cancel the request
    if request.session.get("student_id") != swap_request.sender.id:
        messages.error(request, "You are not authorized to cancel this request.")
        return redirect("swap_requests")

    swap_request.delete()  # Removes the request from the database

    messages.success(request, "Swap request canceled successfully.")
    return redirect("swap_requests")

#................................................................................................................................................................................