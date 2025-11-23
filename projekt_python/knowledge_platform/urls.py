# knowledge_platform/urls.py
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.contrib.auth import views as auth_views
from quizzes import views as quiz_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quizzes/', include('quizzes.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='quizzes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # ← без template_name
    path('register/', quiz_views.register, name='register'),
    path('', lambda request: redirect('quizzes:quiz_list'), name='home'),
]