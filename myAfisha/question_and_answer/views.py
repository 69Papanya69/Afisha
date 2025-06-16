from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Question
from .serializers import QuestionSerializer

# Create your views here.

class LastQuestionListView(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.order_by('-created_at')[:3]
