from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserView, PerformanceViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'performances', PerformanceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/user/', UserView.as_view(), name='user'),
    path('api/', include('perfomance.urls')),
    path('api/', include('users.urls')),  # Добавлен маршрут для пользовательских API
    path('api/', include(router.urls)),
    path('api/', include('question_and_answer.urls')),
]

# Подключаем Django Silk для профилирования и отладки
if settings.DEBUG:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]

# Подключаем статические файлы
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)