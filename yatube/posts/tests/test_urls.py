from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.tests.help_func import check_status_code

User = get_user_model()


class TaskURLTests(TestCase):
    """Тестирование работоспособности URL-адресов"""

    @classmethod
    def setUpClass(cls):
        """"создаем тестовую запись,
            формируем необходимые переменные и кортежи
        """
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.index = ('posts:index', None)
        cls.group_list = (
            'posts:group_list',
            [cls.group.slug]
        )
        cls.post_detail = (
            'posts:post_detail',
            [cls.post.id]
        )
        cls.profile = (
            'posts:profile',
            [cls.author.username]
        )
        cls.post_create = ('posts:post_create', None)
        cls.post_edit = (
            'posts:post_edit',
            [cls.post.id]
        )
        cls.add_comment = ('posts:add_comment', [cls.post.id])
        f'/posts/{cls.post.id}/comment/'
        cls.unknown_page = '/some_page/'
        cls.pages_available_for_guests = [
            cls.index,
            cls.group_list,
            cls.profile,
            cls.post_detail,
        ]
        cls.pages_available_for_users = [
            *cls.pages_available_for_guests,
            cls.post_create
        ]
        cls.pages_for_redirect_guests = [
            cls.post_create,
            cls.post_edit
        ]
        cls.url_post_edit, cls.args_post_edit = cls.post_edit

    def setUp(self):
        """присваиваем пользователям объект клиента,
            авторизовываем пользователя и автора
        """
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_comments_redirect_user_on_post_detail(self):
        """после написания комментария пользователь перенаправляется
            на страницу публикации.
        """
        url, args = self.add_comment
        url_post, args_post = self.post_detail
        response = self.authorized_author.get(reverse(url, args=args))
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'))

    def test_comments_redirect_anonymous_on_admin_login(self):
        """попытка оставить комментарий перенаправит анонимного
        пользователя на страницу логина.
        """
        url, args = self.add_comment
        response = self.guest_client.get(reverse(url, args=args))
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/comment/')
        )

    def test_pages_exists_at_desired_location_for_guests(self):
        """страницы проекта:
            index, group_list, profile, post_detail
            доступны любому пользователю
        """
        for page, args in self.pages_available_for_guests:
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_exists_at_desired_location_for_users(self):
        """страницы проекта:
            index, group_list, profile, post_detail, post_create
            доступны авторизованным пользователям
        """
        for page, args in self.pages_available_for_users:
            with self.subTest(page=page):
                response = self.authorized_client.get(reverse(page, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_redirect_to_login(self):
        """При попытке создания (редактирования) публикации
            неавторизованный пользователь
            переадресуется на страницу регистрации
        """
        for page, args in self.pages_for_redirect_guests:
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page, args=args))
                check_status_code(self, response)

    def test_post_edit_available_for_author(self):
        """изменение публикации доступно автору"""
        response_auth = self.authorized_author.get(
            reverse(self.url_post_edit, args=self.args_post_edit)
        )
        self.assertEqual(response_auth.status_code, HTTPStatus.OK)

    def test_post_edit_anavailable_for_guest(self):
        """изменение публикации недоступно авторизиорованному пользователю,
            происходит редирект
        """
        response_user = self.authorized_client.get(
            reverse(self.url_post_edit, args=self.args_post_edit)
        )
        check_status_code(self, response_user)

    def test_request_to_unknown_page_return_404(self):
        """запрос к несуществующей странице вернёт ошибку 404"""
        response = self.guest_client.get(self.unknown_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
