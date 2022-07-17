import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post
from posts.tests.help_func import check_labels, check_labels_comments

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Тестирование Формы"""
    @classmethod
    def setUpClass(cls):
        """"создаем тестовую запись"""
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='test comment',
        )
        cls.post_create = ['posts:post_create', None]
        cls.profile = ['posts:profile', [cls.author.username]]
        cls.post_edit = ['posts:post_edit', [cls.post.id]]
        cls.post_detail = ['posts:post_detail', [cls.post.id]]
        cls.date_of_publication_post = 'pub_date'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """авторизовываем автора"""
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        """Проверка: валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'author': self.author,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_author.post(
            reverse(self.post_create[0]),
            data=form_data,
            follow=True
        )
        url, args = self.profile
        self.assertRedirects(response, reverse(
            url, args=args)
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        check_labels(self)

    def test_post_edit(self):
        """Проверка редактирования записи."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'author': self.author,
            'group': self.group.id
        }
        response = self.authorized_author.post(
            reverse(self.post_edit[0], args=self.post_edit[1]),
            data=form_data,
            follow=True
        )
        url, args = self.post_detail
        self.assertRedirects(response, reverse(
            url, args=args)
        )
        self.assertEqual(Post.objects.count(), posts_count)
        check_labels(self)

    def test_create_comment(self):
        """Проверка: валидная форма отправляет комментарий в Post."""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'test comment',
            'author': self.author,
        }
        response = self.authorized_author.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[self.post.id])
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        check_labels_comments(self)
