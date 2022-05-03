from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from api_yamdb import settings

from .filter import TitleFilter
from .permissions import AuthorOrModerOrReadOnly, IsAdmin, IsAdminOrReaOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer,
                          TitleSerializerPostPatch, TokenSerializer,
                          UserSerializer, UserSignupSerializer)


@api_view(['POST'])
def get_confirmation_code(request):
    serializer = UserSignupSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user, _created = User.objects.get_or_create(username=username, email=email)
    confirmation_code = default_token_generator.make_token(user)

    mail_subject = 'Код подтверждения'
    message = f'Ваш {mail_subject.lower()}: {confirmation_code}'
    sender_email = settings.DEFAULT_FROM_EMAIL
    recipient_email = email
    send_mail(
        mail_subject,
        message,
        sender_email,
        [recipient_email],
        fail_silently=False
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    resp = {'confirmation_code': 'Неверный код подтверждения'}
    return Response(resp, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    permission_classes = [IsAdmin | IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)

    @action(
        methods=['patch', 'get'],
        permission_classes=[IsAuthenticated],
        detail=False,
    )
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        if self.request.method != 'PATCH':
            return Response(serializer.data)
        if user.role == User.USER and not user.is_superuser:
            role = request.data.dict().get('role', None)
            if role is not None and role != 'user':
                _mutable = request.data._mutable
                request.data._mutable = True
                request.data['role'] = 'user'
                request.data._mutable = _mutable
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CreateListDestroyViewSet(ListModelMixin, CreateModelMixin,
                               DestroyModelMixin, viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReaOnly]

    def perform_destroy(self, instance):
        slug = self.kwargs.get('slug')
        obj_destr = get_object_or_404(Category, slug=slug)
        obj_destr.delete()


class GenresViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReaOnly]

    def perform_destroy(self, instance):
        slug = self.kwargs.get('slug')
        obj_destr = get_object_or_404(Genre, slug=slug)
        obj_destr.delete()


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReaOnly]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()

    def perform_destroy(self, instance):
        pk = int(self.kwargs.get('pk'))
        obj_destr = get_object_or_404(Title, pk=pk)
        obj_destr.delete()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializer
        return TitleSerializerPostPatch


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrModerOrReadOnly,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        author = get_object_or_404(
            User,
            username=self.request.user
        )
        serializer.save(
            author=author,
            title=title
        )

    def perform_destroy(self, serializer):
        super().perform_destroy(serializer)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return Review.objects.filter(title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrModerOrReadOnly,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        author = self.request.user
        serializer.save(
            author=author,
            review=review
        )

    def perform_destroy(self, serializer):
        super().perform_destroy(serializer)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()
