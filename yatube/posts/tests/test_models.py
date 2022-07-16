from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Тестирование модели"""
    @classmethod
    def setUpClass(cls):
        """"создаем тестовую запись"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_result = {
            self.group: 'Тестовая группа',
            self.post: 'Тестовая пост'
        }
        for field, expected_values in expected_result.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_values
                )
