from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'app'

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/courses/upload/', views.upload_page, name='upload_page'),
    path('academy/login/', LoginView.as_view(template_name='auth.html', authentication_form=views.CustomLoginForm), name='login'),
    path('academy/logout/', LogoutView.as_view(next_page='app:auth_page'), name='logout'),
    path('academy/register/', views.register, name='register'),
    path('academy/complete/<str:item_type>/<int:item_id>/', views.complete, name='complete'),
    path('academy/courses/', views.courses, name='courses'),
    path('academy/dashboard/', views.dashboard, name='dashboard'),
    path('academy/course/<int:course_id>/', views.course, name='course'),
    path('academy/section/<int:section_id>/', views.section, name='section'),
    path('academy/exercise/<int:exercise_id>/', views.exercise, name='exercise'),
    path('academy/profile/', views.profile, name='profile'),
    path('academy/auth/', views.auth_page, name='auth_page'),
]