from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """"Класс для формы поста"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }


class CommentForm(forms.ModelForm):
    """"Класс для формы комментария"""
    class Meta:
        model = Comment
        fields = ('text',)
        help_text ={
            'text': 'введите комментарий'
        }