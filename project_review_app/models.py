from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# --------------------
# Custom User Model
# --------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_student(self):
        return self.role == 'student'
    DIVISION_CHOICES = (
        ('A', 'Division A'),
        ('B', 'Division B'),
        ('C', 'Division C'),
    )
    SEMESTER_CHOICES = (
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    # Student fields
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES, blank=True, null=True)
    roll_no = models.CharField(max_length=20, blank=True, null=True)
    semester = models.PositiveIntegerField(choices=SEMESTER_CHOICES, blank=True, null=True)

    # Teacher fields
    department = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} (Student) | Roll: {self.roll_no or '-'} | Sem: {self.semester or '-'} | Div: {self.division or '-'}"
        #return f"{self.username} ({self.role})"


# --------------------
# Topic Model
# --------------------
class Topic(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="topics_created"
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="topics_assigned"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# --------------------
# Project Group Model
# --------------------
class ProjectGroup(models.Model):
    name = models.CharField(max_length=120)
    max_members = models.PositiveIntegerField(default=3)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    division = models.CharField(
        max_length=1,
        choices=CustomUser.DIVISION_CHOICES,
        blank=True,
        null=True
    )
    semester = models.PositiveIntegerField(
        choices=CustomUser.SEMESTER_CHOICES,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name



# --------------------
# Group Members
# --------------------
class GroupMember(models.Model):
    group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'student')

    def __str__(self):
        return f"{self.student.username} -> {self.group.name}"


# --------------------
# Submission Model
# --------------------
class Submission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE, related_name='submissions')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='submissions/')
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Submission {self.id} - {self.group.name}"


# --------------------
# Query Model
# --------------------
class Query(models.Model):
    group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE, related_name='queries')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query from {self.student.username} in {self.group.name}"

