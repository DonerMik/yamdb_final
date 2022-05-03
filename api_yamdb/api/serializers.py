from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')

        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')


class TitleSerializerPostPatch(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         many=True,
                                         slug_field='slug')
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='name'
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        method = self.context.get('request').method
        if method != 'POST':
            return super().validate(attrs)

        title_id = self.context.get('view').kwargs['title_id']
        author = self.context.get('request').user
        if Review.objects.filter(
                author=author, title_id=title_id
        ).exists():
            raise ValidationError(
                'Нельзя дважды написать отзыв на одно произведение')
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
