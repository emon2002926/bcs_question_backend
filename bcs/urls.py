from django.urls import path
from .views import ExamListView

urlpatterns = [
    path('exams/', ExamListView.as_view(), name='exam-list'),
]