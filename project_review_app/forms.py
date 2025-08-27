from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from .models import CustomUser, Submission, Topic, ProjectGroup, Query

User = get_user_model()


# --------------------
# Signup Form
# --------------------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    # Student-specific
    division = forms.ChoiceField(choices=CustomUser.DIVISION_CHOICES, required=False)
    roll_no = forms.CharField(required=False)
    semester = forms.ChoiceField(choices=CustomUser.SEMESTER_CHOICES, required=False)

    # Teacher-specific
    department = forms.CharField(required=False)
    subject = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2', 'role',
            'division', 'roll_no', 'semester',
            'department', 'subject'
        ]

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')

        if role == 'student':
            if not cleaned.get('division') or not cleaned.get('roll_no') or not cleaned.get('semester'):
                raise forms.ValidationError("For students: Division, Roll No and Semester are required.")
        elif role == 'teacher':
            if not cleaned.get('department') or not cleaned.get('subject'):
                raise forms.ValidationError("For teachers: Department and Subject are required.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data.get('role', 'student')

        if user.role == 'student':
            user.division = self.cleaned_data['division']
            user.roll_no = self.cleaned_data['roll_no']
            user.semester = self.cleaned_data['semester']
            user.department = None
            user.subject = None
        else:
            user.department = self.cleaned_data['department']
            user.subject = self.cleaned_data['subject']
            user.division = None
            user.roll_no = None
            user.semester = None

        if commit:
            user.save()
        return user


# --------------------
# Auth Form (Login by Email)
# --------------------
class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


# --------------------
# Submission Form
# --------------------
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'note']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# --------------------
# Topic Form
# --------------------
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

# --------------------
# Group Creation Form
# --------------------
class GroupForm(forms.ModelForm):
    class Meta:
        model = ProjectGroup
        fields = ['name', 'max_members', 'topic', 'division', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(GroupForm, self).__init__(*args, **kwargs)
        if user:
         
            self.fields['topic'].queryset = Topic.objects.filter(created_by=user)


# --------------------
# Assign Members Form
# --------------------
class AssignMembersForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        students_qs = kwargs.pop('students_qs', None)
        super().__init__(*args, **kwargs)
        if students_qs is not None:
            self.fields['students'].queryset = students_qs


# --------------------
# Query Form
# --------------------
class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
