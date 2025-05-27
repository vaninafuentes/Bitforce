from rest_framework import serializers
from .models import GymUser

class GymUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}  # oculta el password en la respuesta
        }

    def create(self, validated_data):
        # Usamos pop para sacar el password y pasarlo a set_password()
        password = validated_data.pop('password', None)
        user = GymUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
