from django.contrib import admin
from .models import Question, Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at')
    search_fields = ('user__username', 'text')
    date_hierarchy = 'created_at'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_question_text', 'get_question_author', 'created_at')
    search_fields = ('user__username', 'question__text')
    date_hierarchy = 'created_at'
    
    def get_question_text(self, obj):
        return obj.question.text
    get_question_text.short_description = 'Question Text'
    
    def get_question_author(self, obj):
        return obj.question.user
    get_question_author.short_description = 'Question Author'