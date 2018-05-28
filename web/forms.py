from django.forms.models import ModelForm

from web import models


class UserProfileForm(ModelForm):

    class Meta:
        model = models.UserProfile
        fields = ['name','department','valid_begin_time','valid_end_time']