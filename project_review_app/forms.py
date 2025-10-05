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
        user.role = "student"
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
# Signup Form Teachers 
# --------------------
class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "department", "subject", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "teacher"
        user.division = None
        user.roll_no = None
        user.semester = None
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
        required=True,
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
            user.set_password(password)
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
            if user.role == "teacher":
                # teacher sees only their created topics
                self.fields['topic'].queryset = Topic.objects.filter(created_by=user)
            elif user.role == "student":
                # 🔹 Option 1: student sees all topics
                self.fields['topic'].queryset = Topic.objects.all()

                # 🔹 Option 2 (better): filter by division/semester
                # self.fields['topic'].queryset = Topic.objects.filter(
                #     teacher__isnull=False,
                #     # adjust if you store division/semester in teacher or topic
                # )

        self.fields["topic"].empty_label = "Select a Topic"


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
