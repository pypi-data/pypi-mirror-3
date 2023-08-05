from django.forms import ModelForm
from notes.models import Announcement

class AnnouncementForm(ModelForm):
    class Meta:
        model = Announcement
        fields=['start', 'end', 'content','author']
        
