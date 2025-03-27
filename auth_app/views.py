from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.permissions import AllowAny,IsAuthenticated
import os
import jwt
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from .utils import encrypt_uuid, decrypt_uuid

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_verified=False
            user.save()
            token = PasswordResetTokenGenerator().make_token(user)
            verification_link = f"{request.data.get('base_url', 'http://localhost:8000/api/auth/verify-email')}?uid={encrypt_uuid(str(user.id))}&token={token}"
            print(verification_link)
            send_mail(
                'Verify Your Email',
                f'Click the link to verify your email: {verification_link}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "User registration is completed successfully."}, status=status.HTTP_201_CREATED)
        return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = request.query_params.get('uid') or request.data.get('uid')
            token = request.query_params.get('token') or request.data.get('token')
            print(uid,token)
            user_id = decrypt_uuid(uid)
            user = get_object_or_404(User, id=user_id)

            if PasswordResetTokenGenerator().check_token(user, token):
                user.is_verified = True
                user.save()
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            return Response({"error":f"error while varifying email. {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            if not user.is_verified:
                return Response({"error": "Email not verified."}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'success':True,
                'message': 'Login successful',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username
            }, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response({'error':serializer.errors,'success':False}, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.decorators import api_view
from .utils import decrypt_uuid

@api_view(['POST'])
def verify_token(request):
    token = request.data.get('token', None)
    if not token:
        return Response({'detail': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return Response({'detail': 'Token is valid', 'payload': payload}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    

from rest_framework_simplejwt.tokens import RefreshToken

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            print(refresh_token)
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklists the token using the built-in method
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error during logout: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
