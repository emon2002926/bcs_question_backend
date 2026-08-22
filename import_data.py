import sqlite3
import os
import django

# Tell the script to use your Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from bcs.models import Exam

def import_exams():
    print("Connecting to legacy database...")
    conn = sqlite3.connect('exams_index.sqlite3')
    cursor = conn.cursor()
    
    # Get all the old exams
    cursor.execute("SELECT name, slug, question_count, status FROM exams_index")
    rows = cursor.fetchall()
    
    # Save them into Django
    for row in rows:
        name, slug, question_count, status = row
        Exam.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'question_count': question_count,
                'status': status
            }
        )
        print(f"Imported: {name}")
        
    print("Done! All exams imported successfully.")

if __name__ == '__main__':
    import_exams()