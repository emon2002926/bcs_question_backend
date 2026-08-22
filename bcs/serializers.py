from rest_framework import serializers
from .models import Exam

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['name', 'slug', 'question_count', 'status'] # These are the exact JSON keys you asked for