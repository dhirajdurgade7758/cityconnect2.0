from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from store.models import StoreOffer

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



class StoreOfferForm(forms.ModelForm):
    class Meta:
        model = StoreOffer
        fields = [
            'name', 'description', 'image', 'coins_required', 'offer_type',
            'location_name', 'location_map_url', 'stock', 'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }