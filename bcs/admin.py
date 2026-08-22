from django.contrib import admin
from .models import Exam, Question

# Registering Exam with a custom admin class to show more details
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count', 'status')
    list_filter = ('status',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} # Automatically fills the slug as you type the name

admin.site.register(Exam, ExamAdmin)

# Registering Question with a custom admin class
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_no', 'exam', 'subject', 'question_text')
    list_filter = ('exam', 'subject')
    search_fields = ('question_text', 'exam__name')

admin.site.register(Question, QuestionAdmin)