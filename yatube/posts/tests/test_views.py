from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post
from posts.tests.help_func import check_labels, group_field_check

User = get_user_model()


class PostsViewsTests(TestCase):
    """Тестрирование Views"""
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
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )
        cls.index = ('posts:index', 'posts/index.html', None)
        cls.group_list = (
            'posts:group_list',
            'posts/group_list.html',
            [cls.group.slug]
        )
        cls.post_detail = (
            'posts:post_detail',
            'posts/post_detail.html',
            [cls.post.id]
        )
        cls.profile = (
            'posts:profile',
            'posts/profile.html',
            [cls.author.username]
        )
        cls.post_create = ('posts:post_create', 'posts/create_post.html', None)
        cls.post_edit = (
            'posts:post_edit',
            'posts/create_post.html',
            [cls.post.id]
        )
        cls.unknown_page = (
            '/some_page/',
            'core/404.html',
        )
        cls.adresses = [
            cls.index,
            cls.group_list,
            cls.profile,
            cls.post_detail,
            cls.post_create,
            cls.post_edit,
        ]
        cls.right_pages = [
            (cls.index[0], cls.index[2]),
            (cls.group_list[0], cls.group_list[2]),
            (cls.profile[0], cls.profile[2])
        ]
        cls.COUNT_OF_POSTS = 2
        cls.page_object = 'page_obj'

    def setUp(self):
        """создаем переменные"""
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.page_obj = 'page_obj'

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template, args in self.adresses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(
                    reverse(reverse_name, args=args)
                )
                self.assertTemplateUsed(response, template)

    def test_pages_404_use_correct_template(self):
        """страница 404 отдает кастомный шаблон"""
        url, template = self.unknown_page
        response = self.guest_client.get(url, follow=True)
        self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context_group_title(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (
            self.authorized_author.get(
                reverse(self.index[0])).context[self.page_obj][0]
        )
        check_labels(self)
        group_field_check(self, response)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_author.get(reverse(self.group_list[0],
                    args=[self.group.slug]))).context[self.page_obj][0]
        check_labels(self)
        group_field_check(self, response)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_author.get(reverse(self.profile[0],
                    args=self.profile[2]))).context[self.page_obj][0]
        check_labels(self)
        group_field_check(self, response)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_author.get(reverse(self.post_detail[0],
                    args=self.post_detail[2]))).context.get('post')
        check_labels(self)
        group_field_check(self, response)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(self.post_create[0]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_get_right_pages(self):
        """проверка, что пост попадает на нужные страницы"""
        Post.objects.create(
            text='new post',
            author=self.author,
            group=self.group
        )

        for url, args in self.right_pages:
            with self.subTest(url=url):
                response = self.authorized_author.get(reverse(url, args=args))
                count_of_posts = len(response.context[self.page_object])
                self.assertEqual(count_of_posts, self.COUNT_OF_POSTS)


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора.
        Создаем тестовые публикации,
        пользователей и переменные
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост1',
            group=cls.group,
        )
        for number in range(2, 14):
            Post.objects.create(
                author=cls.author,
                text='Тестовый пост ' + str(number),
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
        cls.pages_requests = [
            cls.index,
            cls.group_list,
            cls.profile
        ]
        cls.COUNT_OF_POSTS = 10
        cls.page_object = 'page_obj'

    def setUp(self):
        """присваиваем пользователям объект клиента,
            авторизовываем пользователя и автора
        """
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_first_page_contains_ten_records(self):
        """проверка: первые страницы содержат по 10 записей"""
        for url, args in self.pages_requests:
            with self.subTest(url=url):
                response = self.authorized_author.get(
                    reverse(url, args=args)
                )
                self.assertEqual(
                    len(response.context[self.page_object]),
                    self.COUNT_OF_POSTS
                )


class FollowTests(TestCase):
    """тестирование подписок"""
    @classmethod
    def setUpClass(cls):
        """создаем тестовые записи"""
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='follower')
        cls.author_1 = User.objects.create_user(username='author_1')
        cls.author_2 = User.objects.create_user(username='author_2')
        Follow.objects.create(
            user=cls.user_follower,
            author=cls.author_1
        )
        Post.objects.create(
            text='Тестовый пост подписки',
            author=cls.author_1
        )
        cls.follow_index = ('posts:follow_index')
        cls.profile_follow = (
            'posts:profile_follow',
            [cls.author_2.username]
        )
        cls.profile_unfollow = (
            'posts:profile_unfollow',
            [cls.author_1.username]
        )
        cls.page_obj = 'page_obj'

    def setUp(self):
        """создаем переменные"""
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.author_1)

    def test_new_in_follow_page(self):
        """Новый пост появляется в ленте пользователей,
            которые на него подписаны
        """
        url, args = self.profile_follow
        self.client_auth_follower.get(reverse(url, args=args))
        response = self.client_auth_follower.get(reverse(self.follow_index))
        self.assertEqual(
            response.context[self.page_obj][0].author.id,
            self.author_1.id)

    def test_user_can_follow_once(self):
        """пользователь может подписаться на автора,
            при этом не более одного раза
        """
        count_of_follow = Follow.objects.count()
        url, args = self.profile_follow
        for follow in range(2):
            self.client_auth_follower.get(reverse(url, args=args))
        self.assertEqual(Follow.objects.count(), count_of_follow + 1)

    def test_user_can_unfollow(self):
        """пользователь может отписаться от автора"""
        count_of_follow = Follow.objects.count()
        url, args = self.profile_unfollow
        self.client_auth_follower.get(reverse(url, args=args))
        self.assertEqual(Follow.objects.count(), count_of_follow - 1)
