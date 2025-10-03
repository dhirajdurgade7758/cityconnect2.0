from django import forms
from issues.models import IssuePost, Task, Comment


class IssuePostForm(forms.ModelForm):
    class Meta:
        model = IssuePost
        fields = ['title', 'description', 'image', 'department',"reported_latitude", "reported_longitude"] # Added 'department'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Pothole on Main Street'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the issue in detail.'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}), # Bootstrap select class
            "reported_latitude": forms.HiddenInput(),
            "reported_longitude": forms.HiddenInput(),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_type', 'proof_image',"reported_latitude", "reported_longitude"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cleaned up local park'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what you did and its impact.'}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'proof_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            "reported_latitude": forms.HiddenInput(),
            "reported_longitude": forms.HiddenInput(),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Add your comment here...'
            })
            
        }

