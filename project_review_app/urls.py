from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # auth
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # teacher
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/view-students/', views.view_students, name='view_students'),
    path('teacher/create-topic/', views.create_topic, name='create_topic'),
    path('teacher/create-group/', views.create_group, name='create_group'),
    path('teacher/group/<int:group_id>/assign/', views.assign_members, name='assign_members'),
    path('teacher/submissions/', views.submissions_list, name='submissions_list'),
    path('teacher/submission/<int:sub_id>/review/', views.review_submission, name='review_submission'),

    #grp crud
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),

    #topic crud
    path('topics/<int:pk>/edit/', views.edit_topic, name='edit_topic'),
    path('topics/<int:pk>/delete/', views.TopicDeleteView.as_view(), name='delete_topic'),
    path("topics/<int:pk>/", views.topic_detail, name="topic_detail"),
    path('teacher/view-students/<int:student_id>/', views.student_detail, name='student_detail'),
    path("topics/", views.topics_list, name="topics_list"),

    

    # student
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/my-group/', views.my_group, name='my_group'),
    path('project-submission/', views.project_submission, name='project_submission'),
    path('my-submissions/', views.view_submissions, name='view_submissions'),
    path('profile/', views.profile, name='profile'),
    path('help-center/', views.help_center, name='help_center'),

]
