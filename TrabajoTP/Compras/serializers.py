from rest_framework import serializers
from django.contrib.auth.models import User # El User de Django
from django.contrib.auth.password_validation import validate_password # Para contraseñas seguras

class RegisterSerializer(serializers.ModelSerializer):
    # Pedimos la contraseña dos veces para confirmar
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmar Contraseña")
    first_name = serializers.CharField(required=True, label="Nombre")
    last_name = serializers.CharField(required=True, label="Apellido")
    email = serializers.EmailField(required=True, label="Email")

    class Meta:
        # ⬇️ 'model' y 'fields' están indentados DENTRO de Meta (2 niveles)
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True}
        }

    # ⬇️ 'validate' y 'create' están indentados (1 nivel),
    #    al mismo nivel que 'class Meta'
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password']) 
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    """
    Serializador para el login de usuarios.
    No usa ModelSerializer porque no está atado a un modelo.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

   

    
   