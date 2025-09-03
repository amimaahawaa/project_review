from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from .forms import *


# --------------------
# Static pages
# --------------------
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


# --------------------
# Authentication
# --------------------
def student_signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # auto-login (safe because we know the password just set)
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                messages.success(request, "Welcome! Your student account is ready.")
                return redirect('home')
            messages.info(request, "Account created. Please login.")
            return redirect('login')
    else:
        form = StudentSignUpForm()
    return render(request, 'signup.html', {'form': form, 'signup_title': 'Student Sign Up Only'})


def login_view(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                user_obj = CustomUser.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    return redirect('home')
                else:
                    form.add_error('password', 'Incorrect password')
            except CustomUser.DoesNotExist:
                form.add_error('username', 'No account found with this email')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

#admin dashboard

@login_required(login_url="admin_login")
def dashboard_view(request):
    if not (request.user.is_superuser or request.user.role == "admin"):
        return redirect("home")   # non-admin ko hata do

    total_teachers = CustomUser.objects.filter(role="teacher").count()
    total_students = CustomUser.objects.filter(role="student").count()
    total_admins = CustomUser.objects.filter(role="admin").count()

    return render(request, "admin/dashboard.html", {
        "total_teachers": total_teachers,
        "total_students": total_students,
        "total_admins": total_admins,
    })





def admin_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser or user.role == "admin":
                login(request, user)
                return redirect("dashboard")
            else:
                form.add_error(None, "You are not authorized as admin.")
    return render(request, "admin_login.html", {"form": form})




def admin_logout(request):
    logout(request)
    return redirect("admin_login") 


def manage_admins(request):
    admins = CustomUser.objects.filter(role="admin")  # sirf admins dikhayenge
    return render(request, "admin/manage_admins.html", {"admins": admins})

def add_admin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = CustomUser.objects.create_user(
                email=email, username=username, password=password, role="admin"
            )
            messages.success(request, "Admin added successfully!")
            return redirect("manage_admins")
    return render(request, "admin/add_admin.html")

def edit_admin(request, admin_id):
    admin = get_object_or_404(CustomUser, id=admin_id)  # 👈 User ki jagah CustomUser lo
    if request.method == "POST":
        form = AdminForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            return redirect("manage_admins")
    else:
        form = AdminForm(instance=admin)
    return render(request, "admin/edit_admin.html", {"form": form, "admin": admin})


def delete_admin(request, admin_id):
    admin = get_object_or_404(CustomUser, id=admin_id, role="admin")
    
    if request.method == "POST":
        admin.delete()
        messages.success(request, "Admin deleted successfully!")
        return redirect("manage_admins")
    
    return render(request, "admin/delete_admin.html", {"admin": admin})

# ---- TEACHERS CRUD ----
def manage_teachers(request):
    teachers = CustomUser.objects.filter(role="teacher")
    return render(request, "admin/manage_teachers.html", {"teachers": teachers})



def add_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully!")
            return redirect("admin_dashboard")
    else:
        form = TeacherForm()
    return render(request, "admin/add_teacher.html", {"form": form})

def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(CustomUser, id=teacher_id, role="teacher")
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect("manage_teachers")
    else:
        form = TeacherForm(instance=teacher)
    return render(request, "admin/edit_teacher.html", {"form": form})


def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(CustomUser, id=teacher_id, role="teacher")
    if request.method == "POST":
        teacher.delete()
        return redirect("manage_teachers")
    return render(request, "admin/confirm_delete.html", {"teacher": "teacher"})


# ---- STUDENTS CRUD ----

def manage_students(request):
    students = CustomUser.objects.filter(role="student")
    return render(request, "admin/manage_students.html", {"students": students})

def edit_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role="student")
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect("manage_students")
    else:
        form = StudentForm(instance=student)
    return render(request, "admin/edit_student.html", {"form": form})


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role="student")
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("manage_students")
    return render(request, "admin/confirm_delete.html", {"object": student, "type": "Student"})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    """Redirect user based on role"""
    if request.user.role == 'teacher':
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


# --------------------
# Role decorators
# --------------------
def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_teacher:
            raise PermissionDenied("Only teachers can access this page")
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    return user_passes_test(lambda u: u.role == 'student')(login_required(view_func))


# --------------------
# Teacher Views
# --------------------
@teacher_required
def teacher_dashboard(request):
    teacher = request.user  
    context = {
        "students_count": CustomUser.objects.filter(role="student").count(),
        "topics_count": Topic.objects.filter(created_by=teacher).count(),
        "groups_count": ProjectGroup.objects.filter(topic__created_by=teacher).count(),
        "pending_reviews_count": Submission.objects.filter(
            status="pending",
            group__topic__created_by=teacher
        ).count(),
    }
    return render(request, "teacher_dashboard.html", context)


@teacher_required
def view_students(request):
    students = CustomUser.objects.filter(role='student').order_by('semester', 'division', 'roll_no')
    semester = request.GET.get('semester')
    division = request.GET.get('division')

    if semester:
        students = students.filter(semester=semester)
    if division:
        students = students.filter(division=division)

    return render(request, 'teacher/view_students.html', {
        'students': students,
        'current_semester': semester or '',
        'current_division': division or '',
        'semester_choices': CustomUser.SEMESTER_CHOICES,
        'division_choices': CustomUser.DIVISION_CHOICES
    })


@teacher_required
def submissions_list(request):
    subs = Submission.objects.all().order_by('-submitted_at')
    return render(request, 'teacher/submissions_list.html', {'subs': subs})


@teacher_required
def review_submission(request, sub_id):
    sub = get_object_or_404(Submission, id=sub_id)
    if request.method == 'POST':
        sub.status = request.POST.get('status')
        sub.feedback = request.POST.get('feedback', '').strip()
        sub.reviewed_at = timezone.now()
        sub.save()
        messages.success(request, 'Submission reviewed successfully.')
        return redirect('submissions_list')
    return render(request, 'teacher/review_submission.html', {'sub': sub})


# ---- Topic CRUD ----
@teacher_required
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('topics_list')
    else:
        form = TopicForm()
    return render(request, 'teacher/create_topic.html', {'form': form})

@teacher_required
def topics_list(request):
    topics = Topic.objects.filter(created_by=request.user)
    return render(request, 'teacher/topics_list.html', {'topics': topics, 'title': 'My Topics'})

@teacher_required
def edit_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect('topics_list')
    else:
        form = TopicForm(instance=topic)
    return render(request, 'teacher/topic_form.html', {'form': form})

class TopicDeleteView(DeleteView):
    model = Topic
    template_name = 'teacher/topic_confirm_delete.html'
    success_url = reverse_lazy('topics_list')

    def get_queryset(self):
        return Topic.objects.filter(created_by=self.request.user)

def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    return render(request, "teacher/topic_detail.html", {"topic": topic})


# ---- Group CRUD ----
@login_required
def group_list(request):
    groups = ProjectGroup.objects.filter(teacher=request.user)
    return render(request, 'teacher/group_list.html', {'groups': groups})

def group_detail(request, pk):
    group = get_object_or_404(ProjectGroup, id=pk)
    members = group.members.select_related("student")
    return render(request, 'teacher/group_detail.html', {'group': group, 'members': members})

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST, user=request.user)
        if form.is_valid():
            group = form.save(commit=False)
            group.teacher = request.user
            group.save()
            messages.success(request, "Group created successfully!")
            return redirect("assign_members", group_id=group.id)
    else:
        form = GroupForm(user=request.user)
    return render(request, 'teacher/create_group.html', {'form': form})

@teacher_required
def group_update(request, pk):
    group = get_object_or_404(ProjectGroup, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_detail', pk=group.id)
    else:
        form = GroupForm(instance=group)
    return render(request, 'teacher/create_group.html', {'form': form, 'title': 'Edit Group'})

class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ProjectGroup
    template_name = 'teacher/group_confirm_delete.html'
    success_url = reverse_lazy('group_list')

    def test_func(self):
        return self.request.user.role == 'teacher'

@teacher_required 
def assign_members(request, group_id):
    group = get_object_or_404(ProjectGroup, id=group_id)
    current_members = group.members.values_list('student_id', flat=True)

    sel_semester = request.GET.get('semester')
    sel_division = request.GET.get('division')

    students = CustomUser.objects.filter(role='student')
    if sel_semester:
        students = students.filter(semester=sel_semester)
    if sel_division:
        students = students.filter(division=sel_division)

    if request.method == 'POST':
        form = AssignMembersForm(request.POST, students_qs=students)
        if form.is_valid():
            group.members.all().delete()
            for student in form.cleaned_data['students']:
                GroupMember.objects.create(group=group, student=student)
            messages.success(request, 'Members updated successfully!')
            return redirect('group_detail', pk=group.id)
    else:
        form = AssignMembersForm(students_qs=students, initial={'students': current_members})

    return render(request, 'teacher/assign_members.html', {
        'form': form,
        'group': group,
        'action_url': reverse('assign_members', args=[group.id]),
        'semester_choices': CustomUser.SEMESTER_CHOICES,
        'division_choices': CustomUser.DIVISION_CHOICES,
        'sel_semester': sel_semester,
        'sel_division': sel_division,
    })


# --------------------
# Student Views
# --------------------
@student_required
def student_dashboard(request):
    return render(request, "student_dashboard.html")


@student_required
def my_group(request):
    student = request.user
    group_memberships = GroupMember.objects.filter(student=student).select_related("group")

    if not group_memberships.exists():
        return render(request, "student/my_group.html")

    groups_data = []
    for gm in group_memberships:
        group = gm.group
        members = group.members.select_related("student")
        groups_data.append({
            "group": group,
            "members": members,
            "topic": group.topic,
            "teacher": group.teacher,
        })

    return render(request, "student/my_group.html", {"groups_data": groups_data})


@student_required
def project_submission(request):
    member = GroupMember.objects.filter(student=request.user).select_related('group').first()
    group = member.group if member else None
    form = SubmissionForm()
    return render(request, 'student/project_submission.html', {'group': group, 'form': form})


@student_required
def submit_project(request):
    if request.method == 'POST':
        member = GroupMember.objects.filter(student=request.user).select_related('group').first()
        if not member:
            messages.error(request, 'You are not assigned to any group yet.')
            return redirect('student_dashboard')

        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.group = member.group
            sub.uploaded_by = request.user
            sub.save()
            messages.success(request, 'Project submitted successfully.')
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Submission failed. Please check the form.')
            return redirect('my_group')
    return redirect('my_group')


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    return render(request, 'teacher/student_detail.html', {'student': student})


def view_submissions(request):
    return render(request, "student/view_submissions.html")

def profile(request):
    return render(request, "student/profile.html")

def help_center(request):
    return render(request, "student/help_center.html")