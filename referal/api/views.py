import random
import time

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer


def check_required_fields(request, fields):
    # Проверка обязательных полей
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

    user, created = CustomUser.objects.get_or_create(phone_number=request.data.get('phone_number'))
    user.is_authenticated = False  # True, когда введет код
    user.save()

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

    received_code = request.data.get('authorization_code')
    if received_code != user.authorization_code:
        return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_authenticated = True
    user.save()
    return Response({'message': 'Authenticated successfully'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def profile(request):
    # Если бы были токены, то:
    # profile = CustomUser.objects.get(phone_number=request.user.phone_number)
    # Получение профиля по телефону
    try:
        profile = CustomUser.objects.get(phone_number=request.data.get('phone_number'))
    except CustomUser.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Проверяем, что инвайт код еще не добавлен
        invite_code = request.data.get('invite_code')
        if profile.invite_code:
            return Response({'error': 'Invite code already added'}, status=status.HTTP_400_BAD_REQUEST)
        if not invite_code:
            return Response({'error': 'Invite code is required'}, status=status.HTTP_400_BAD_REQUEST)
        return activate_invite_code(profile, invite_code)


def activate_invite_code(profile, invite_code):
    # Проверяем, существует ли пользователь с указанным инвайт-кодом
    try:
        inviter = CustomUser.objects.get(invite_code=invite_code)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid invite code'}, status=status.HTTP_400_BAD_REQUEST)
    profile.inviter = inviter
    profile.save()
    return Response({'message': 'Invite code added successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def invites_counter(request):
    try:
        user = CustomUser.objects.get(phone_number=request.data.get('phone_number'))
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    # Получение всех, кого пользователь пригласил
    invited = user.invitees.all()
    # Получение списка номеров телефонов приглашенных пользователей
    invited_users_phones = [invitee.phone_number for invitee in invited]
    return Response({'invited_users': invited_users_phones}, status=status.HTTP_200_OK)
