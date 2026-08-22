from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Exam
from .serializers import ExamSerializer

class ExamListView(APIView):
    # This ensures the Flutter app must provide a valid access token!
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)