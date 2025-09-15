from django import forms
from .models import Election, Candidate, CandidateField, User

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CandidateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=False, help_text="Optional: Enter the username of a registered user to link them to this candidate.")

    class Meta:
        model = Candidate
        fields = ['full_name', 'bio', 'image', 'username']
        labels = {
            'bio': 'Info',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username does not exist.")
        return username

class CandidateFieldForm(forms.ModelForm):
    class Meta:
        model = CandidateField
        fields = ['name', 'value']