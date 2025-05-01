# app/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'app'

urlpatterns = [
    path('admin/courses/upload/', views.upload_page, name='upload_page'),
    path('auth/login/', LoginView.as_view(template_name='app/auth.html', authentication_form=views.CustomLoginForm), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', views.register, name='register'),
    path('course/complete/<str:item_type>/<int:item_id>/', views.complete, name='complete'),
    path('academy/courses/', views.courses, name='courses'),
    path('academy/dashboard/', views.dashboard, name='dashboard'),
    path('academy/courses/course/<int:course_id>/', views.course, name='course'),
    path('academy/courses/section/<int:section_id>/', views.section, name='section'),
    path('academy/courses/exercise/<int:exercise_id>/', views.exercise, name='exercise'),
    path('academy/courses/profile/', views.profile, name='profile'),
    path('academy/auth/', views.auth_page, name='auth_page'),
]
