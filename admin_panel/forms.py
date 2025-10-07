from django import forms
from django.contrib.auth.forms import AuthenticationForm

class DepartmentAdminLoginForm(AuthenticationForm):
    # Add a hidden field or just reuse username & password form
    pass

from issues.models import IssuePost

class ResolveIssueForm(forms.ModelForm):
    class Meta:
        model = IssuePost
        fields = ['status', 'resolved_description', 'resolved_image']
        widgets = {
            'resolved_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the resolution or remarks...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
