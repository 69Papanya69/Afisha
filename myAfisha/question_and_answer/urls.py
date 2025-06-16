from django.urls import path
from .api_views import LastQuestionListView

urlpatterns = [
    path('questions/last/', LastQuestionListView.as_view(), name='question-last'),
]
