from rest_framework.generics import ListAPIView
from .models import Question
from .serializers import QuestionSerializer

class LastQuestionListView(ListAPIView):
    serializer_class = QuestionSerializer
    def get_queryset(self):
        return Question.objects.order_by('-created_at')[:3]
