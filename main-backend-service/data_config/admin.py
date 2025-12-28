# data_config/admin.py
from django import forms
from django.contrib import admin

from chat_config.models import Chat
from .models import Prompt


class ChatIdModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.id)  

class PromptAdminForm(forms.ModelForm):
    chat_id = ChatIdModelChoiceField(queryset=Chat.objects.all())

    class Meta:
        model = Prompt
        fields = '__all__'

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    form = PromptAdminForm
