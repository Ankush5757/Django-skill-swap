from .models import Student, Profile_Pic

def user_profile(request):
    if "student_id" in request.session:
        student_id = request.session.get("student_id")
        student = Student.objects.filter(id=student_id).first()
        profile_pic = Profile_Pic.objects.filter(student=student).first()

        first_name = student.name.split()[0] if student else None

        return {
            "first_name": first_name,
            "profile_pic": profile_pic,
        }
    return {"first_name": None, "profile_pic": None}
