from django.db import models

class Question(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='questions', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    text = models.TextField(verbose_name='Текст')
    
    class Meta:
        verbose_name='Вопрос'
        verbose_name_plural = "Вопросы"
        
    
    def __str__(self):
        return f"Question by {self.user.username}"
    

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='answers', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    text = models.TextField(verbose_name='Текст')
    
    
    class Meta:
        verbose_name='Ответ'
        verbose_name_plural = "Ответы"
    
    
    def __str__(self):
        return f"Answer by {self.user.username} to {self.question.id}"