import os
import sys

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import CustomUser

sys.path.append(os.path.abspath('..'))

BLOCK_USERNAME = ['me']
REGULAR_EXPR = r'^[\w.@+-]+$'
SCORE_RANGE = 11


class RegistrationSerializer(serializers.ModelSerializer):

    def validate(self, data):
        for block_name in BLOCK_USERNAME:
            if (
                    data['username'] in block_name
                    or CustomUser.objects.filter(username=block_name).exists()
            ):
                raise serializers.ValidationError(
                    f"Нельзя использовать имя - {data['username']}"
                )

            if (
                    CustomUser.objects.filter(
                        email=f'{block_name}{REGULAR_EXPR}'
                    ).exists()
                    or block_name in data['email']
            ):
                raise serializers.ValidationError(
                    f"В названии почты - {data['email']} - содержатся "
                    f"недопустимые выражения"
                )
            return data

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
        )


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, )
    confirmation_code = serializers.CharField(required=True, )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'confirmation_code'
        )


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug'
        )
        model = Genre


class TitlesPostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitlesGetSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class ReviewsSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    def validate_score(self, value):
        if value not in range(SCORE_RANGE):
            raise serializers.ValidationError(
                'Оценка некорректна, выберите число от 1 до 10'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentsSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = CustomUser


class UserMySelfSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField()
    role = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = CustomUser
