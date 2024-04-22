from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer
import random
import time


def check_required_fields(request, fields):
    for field in fields:
        if not request.data.get(field):
            return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
    return None

@api_view(['POST'])
def send_code(request):
    error_response = check_required_fields(request, ['phone_number'])
    if error_response:
        return error_response

    time.sleep(2)
    auth_code = ''.join(random.choices('0123456789', k=4))

    # Создание пользователя или обновление существующего
    user, created = CustomUser.objects.get_or_create(phone_number=request.data.get('phone_number'))
    user.is_authenticated = False  # Пользователь авторизуется с помощью кода
    user.save()

    # Сохранение кода аутентификации в объект пользователя
    user.authorization_code = auth_code
    user.save()

    return Response({'authorization_code': auth_code}, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_code(request):
    error_response = check_required_fields(request, ['phone_number', 'authorization_code'])
    if error_response:
        return error_response

    try:
        user = CustomUser.objects.get(phone_number=request.data.get('phone_number'))
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_authenticated:
        return Response({'error': 'User already authenticated'}, status=status.HTTP_400_BAD_REQUEST)

    # Проверка кода аутентификации
    received_code = request.data.get('authorization_code')
    if received_code != user.authorization_code:
        return Response({'error': 'Invalid authorization code'}, status=status.HTTP_400_BAD_REQUEST)

    # Пользователь успешно аутентифицирован
    user.is_authenticated = True
    user.save()

    return Response({'message': 'User authenticated successfully'}, status=status.HTTP_200_OK)