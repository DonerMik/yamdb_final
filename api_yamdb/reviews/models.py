from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    validate_slug)
from django.db import models

from .validators import year_validator


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    ]

    username = models.CharField(max_length=191, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True,
                           verbose_name='Биография',
                           )

    role = models.CharField(
        max_length=20,
        choices=ROLE,
        default=USER,
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(models.Model):
    name = models.CharField(max_length=256,
                            db_index=True,
                            verbose_name='Категория')
    slug = models.SlugField(unique=True,
                            max_length=50,
                            blank=True,
                            null=True,
                            validators=[validate_slug])

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'


class Genre(models.Model):
    name = models.CharField(max_length=256,
                            db_index=True,
                            verbose_name='Жанр')
    slug = models.SlugField(unique=True,
                            max_length=50,
                            blank=True,
                            null=True,
                            validators=[validate_slug])

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name_plural = 'Жанры'
        verbose_name = 'Жанр'


class Title(models.Model):
    name = models.CharField(max_length=256,
                            verbose_name='Произведение',
                            )
    year = models.IntegerField(validators=[year_validator],
                               db_index=True)
    description = models.TextField(blank=True, default='не заполнено')
    genre = models.ManyToManyField(Genre, blank=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='titles')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Произведения'
        verbose_name = 'Произведение'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now=True)

    class Meta:
        verbose_name_plural = 'Отзывы'
        verbose_name = 'Отзыв'
        ordering = ('-pub_date',)
        unique_together = ('author', 'title')
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарии'
        ordering = ('-pub_date',)
