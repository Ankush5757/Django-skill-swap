from django.db import models
from Accounts.models import Student

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserSkill(models.Model):
    SKILL_TYPE_CHOICES = [
        ('teach', 'Teach'),
        ('learn', 'Learn'),
        ('volunteer', 'Volunteer')
    ]

    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    student = models.ForeignKey(Student, related_name='user_skills', on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, related_name='user_skills', on_delete=models.CASCADE)
    skill_type = models.CharField(max_length=15, choices=SKILL_TYPE_CHOICES)

    # Proficiency level should be required for both 'teach' and 'volunteer'
    skill_proficiency = models.CharField(
        max_length=15, choices=PROFICIENCY_CHOICES, blank=True, null=True
    )

    class Meta:
        unique_together = ('student', 'skill', 'skill_type')

    def save(self, *args, **kwargs):
        # Proficiency required for 'teach' and 'volunteer'
        if self.skill_type in ['teach', 'volunteer'] and not self.skill_proficiency:
            raise ValueError("Proficiency is required for teaching and volunteering skills.")
        super().save(*args, **kwargs)

    def __str__(self):
        proficiency_display = f" ({self.skill_proficiency})" if self.skill_proficiency else ""
        return f"{self.student.name} - {self.skill.name} ({self.skill_type}){proficiency_display}"




class SwapRequest(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="received_requests")
    skill = models.ForeignKey(UserSkill, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("sender", "receiver", "skill")  # Prevent duplicate active requests

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.skill}) - {self.status}"
