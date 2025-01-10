from django import forms
from .models import UserProfile

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['custom_username']
        labels = {'custom_username': 'New Username'}
        widgets = {
            'custom_username': forms.TextInput(attrs={'placeholder': 'Enter your new username'}),
        }

    def clean_custom_username(self):
        custom_username = self.cleaned_data.get('custom_username')
        if not custom_username:
            raise forms.ValidationError("Username cannot be empty.")
        return custom_username
