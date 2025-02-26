from django.contrib import admin
from . models import Skill, UserSkill, SwapRequest

# Register your models here.

admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(SwapRequest)

