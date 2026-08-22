from django.db import models

# 1. CATEGORY: This will hold "BCS Question Bank", "Bank Question Bank", etc.
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

# 2. EXAM: This maps to your exams_index.sqlite3 file (e.g., "50th BCS")
class Exam(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    question_count = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='published')
    
    def __str__(self):
        return self.name

# 3. QUESTION: This maps to your all_bcs_questions.sqlite3 file
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_no = models.CharField(max_length=50) # Using CharField in case of "1a", "1b" etc.
    subject = models.CharField(max_length=100) # e.g., "English", "Math", "GK"
    
    question_text = models.TextField()
    question_images = models.TextField(blank=True, null=True) # Storing image URLs or paths
    
    option_a_text = models.CharField(max_length=500, blank=True, null=True)
    option_a_image = models.TextField(blank=True, null=True)
    
    option_b_text = models.CharField(max_length=500, blank=True, null=True)
    option_b_image = models.TextField(blank=True, null=True)
    
    option_c_text = models.CharField(max_length=500, blank=True, null=True)
    option_c_image = models.TextField(blank=True, null=True)
    
    option_d_text = models.CharField(max_length=500, blank=True, null=True)
    option_d_image = models.TextField(blank=True, null=True)
    
    correct_answer = models.CharField(max_length=10) # e.g., "A", "B", "C", "D"
    
    explanation = models.TextField(blank=True, null=True)
    explanation_images = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.exam.name} - Q{self.question_no}"