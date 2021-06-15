from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForComment(UserSerializerForTweet):
    pass

class UserSerializerForFriendship(UserSerializerForTweet):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'User does not exist.'
            })
        return data


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User #指定model是谁
        fields = ('username', 'email', 'password') #白名单模式，model中即使有其他属性，也不添加；只添加fields

    # will be called when is_valid is called
    def validate(self, data):
        # TODO<HOMEWORK> 增加验证 username 是不是只由给定的字符集合构成
        if User.objects.filter(username=data['username'].lower()).exists(): #存储时就是小写
            raise exceptions.ValidationError({
                'username': 'This username has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user