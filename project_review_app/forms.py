from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from .models import CustomUser, Submission, Topic, ProjectGroup, Query

User = get_user_model()


# --------------------
# Signup Form Students 
# --------------------

class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "semester",
            "division",
            "roll_no",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        # FORCE student role (POST me kuch bhi aaye, yahi set hoga)
        user.role = "student"
        # teacher-only fields kabhi mat chhedo
        user.department = None
        user.subject = None
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('division') or not cleaned.get('roll_no') or not cleaned.get('semester'):
            raise forms.ValidationError("Division, Roll No and Semester are required.")
        return cleaned


# --------------------
# Signup Form teachers 
# --------------------
class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "department", "subject", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "teacher"   # force teacher role
        # student fields blank kar do
        user.division = None
        user.roll_no = None
        user.semester = None
        # password hash set karna zaroori hai
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
class AdminStudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "roll_no", "semester", "division", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "student"
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class AdminForm(forms.ModelForm):
    password = forms.CharField(
        required=True,   # 👈 ab blank nahi chhod sakte
        widget=forms.PasswordInput,
        help_text="Enter a strong password."
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)  # ✅ always hashed password save karega

        # Force admin role + staff permission
        user.role = "admin"
        user.is_staff = True   

        if commit:
            user.save()
        return user



# ---------- Teacher Edit Form (Admin ke liye edit/update) ----------
class TeacherEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "department", "subject")


# ---------- Student Edit Form (Admin ke liye edit/update) ----------
class StudentForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "roll_no", "semester", "division")

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
