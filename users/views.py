from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UpdateUserProfileSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .serializers import ProfileSerializer
from rest_framework import generics

class TestView(APIView):
    def get(self, request):
        return Response({"message": "¡Bienvenido de nuevo!"}, status=status.HTTP_200_OK)

class ValidateTokenView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Si llegamos aquí, el token es válido porque el decorator IsAuthenticated lo validó
        return Response({
            "valid": True,
            "user_id": request.user.id,
            "username": request.user.username
        }, status=status.HTTP_200_OK)

class RegisterAPIView(APIView):
    def post(self, request):
        print("Datos recibidos:", request.data)
        print(request.data.get('email'))
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print("Usuario registrado:", user)
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Usuario registrado con éxito',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalida el token
            return Response({"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Usuario eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)


class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateUserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario y perfil actualizados correctamente'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Contraseña actualizada correctamente'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email)
        print(User.objects.values_list('email', flat=True))
        user = get_object_or_404(User, email=email)
        print(user.pk)
        
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:5173/reset-password/{user.pk}/{token}"
        print(reset_link)
        
        send_mail(
            subject="Restablecer tu contraseña",
            message=f"Haz clic en el enlace para cambiar tu contraseña: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )

        return Response({"message": "Correo enviado"}, status=status.HTTP_200_OK)

    
class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            # Intentamos obtener el usuario usando el id que recibimos en el enlace
            user = get_object_or_404(User, pk=uidb64)

            # Verificamos si el token es válido
            if not default_token_generator.check_token(user, token):
                return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

            # Obtenemos la nueva contraseña
            new_password = request.data.get('password')
            if not new_password:
                return Response({"error": "La nueva contraseña es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

            # Validar que la nueva contraseña sea suficientemente segura
            if len(new_password) < 8:
                return Response({"error": "La contraseña debe tener al menos 8 caracteres"}, status=status.HTTP_400_BAD_REQUEST)

            # Si todo es correcto, actualizamos la contraseña del usuario
            print("Antes:", user.password)
            user.set_password(new_password)
            user.save()
            print("Después:", user.password)
            return Response({"message": "Contraseña cambiada exitosamente"}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
