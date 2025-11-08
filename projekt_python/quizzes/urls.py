from django.urls import path
from . import views


app_name = "quizzes"

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("quiz/<int:pk>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<int:pk>/submit/", views.quiz_submit, name="quiz_submit"),
]




