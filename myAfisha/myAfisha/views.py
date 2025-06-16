from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from perfomance.models import Performance
from perfomance.serializers import PerformanceSerializer

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer


class UserView(APIView):
    permission_classes = [IsAuthenticated]  # Требуем аутентификацию

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'registrationDate': user.date_joined,  # Дата регистрации
            'is_admin': getattr(user, 'is_admin', False),
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
        })

    def put(self, request):
        user = request.user
        username = request.data.get('username', user.username)
        email = request.data.get('email', user.email)

        user.username = username
        user.email = email
        user.save()

        return Response({
            'username': user.username,
            'email': user.email,
            'registrationDate': user.date_joined,
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]  # Разрешаем доступ всем

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response(
                {"error": "All fields (username, email, password) are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, email=email, password=password)
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

