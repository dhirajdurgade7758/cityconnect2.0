from django import forms
from django.contrib.auth.forms import AuthenticationForm

class DepartmentAdminLoginForm(AuthenticationForm):
    # Add a hidden field or just reuse username & password form
    pass
