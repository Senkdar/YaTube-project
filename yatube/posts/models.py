from tkinter import CASCADE
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель группы."""
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='uniqe_URL')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        """Возвращает имя группы."""
        return self.title


class Post(models.Model):
    """Модель записи.
    class Meta -- сортирует записи по дате публикации,
    начиная с последней.
    """
    text = models.TextField(
        help_text="Введите текст записи",
        verbose_name='текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        """выводит текст поста."""
        return self.text

    class Meta:
        """добавляет сортировку публикаций по дате
        и выводимое имя
        """
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'


class Comment (models.Model):
    """Модель комментариев."""
    post = models.ForeignKey(
        Post,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='комменнтарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    text = models.TextField(
        verbose_name='текст',
        help_text='введите текст'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )

    def __str__(self):
        """выводит текст комментария."""
        return self.text

    class Meta:
        """добавляет сортировку комментариев по дате
            и выводимое имя
        """
        ordering = ['-created']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'


class Follow (models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='пользователь'
    )
    author = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='following',
    verbose_name='автор'
    )
