from http import HTTPStatus

from posts.models import Comment, Post


def check_labels_comments(self):
    """фкункция для проверки полей комментария"""
    self.assertEqual(Comment.objects.first().post, self.post)
    self.assertEqual(Comment.objects.first().text, self.comment.text)
    self.assertEqual(Comment.objects.first().author, self.author)


def check_labels(self):
    """фкункция для проверки полей Шаблонов"""
    self.assertEqual(Post.objects.first().group.title, self.group.title)
    self.assertEqual(Post.objects.first().text, self.post.text)
    self.assertEqual(Post.objects.first().author, self.post.author)


def group_field_check(self, group_object):
    """фкункция для проверки полей группы Шаблонов"""
    self.assertEqual(group_object.group.title, self.group.title)
    self.assertEqual(group_object.group.slug, self.group.slug)
    self.assertEqual(group_object.group.description, self.group.description)


def check_status_code(self, page_response):
    """проверка редиректа со страницы
        (код ответа страницы должен быть равен 302)
    """
    self.assertEqual(page_response.status_code, HTTPStatus.FOUND)
