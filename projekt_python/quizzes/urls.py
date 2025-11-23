from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("quiz/<int:pk>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<int:pk>/submit/", views.quiz_submit, name="quiz_submit"),
    path("results/<int:submission_id>/", views.quiz_results, name="quiz_results"),
    path('my-stats/', views.user_statistics, name='user_statistics')
]