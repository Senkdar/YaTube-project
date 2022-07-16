from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginator


@cache_page(20, key_prefix='index_page')
def index(request):
    """Передаёт в шаблон posts/index.html
    десять последних объектов модели Post.
    """
    post_list = (
        Post.objects.select_related('group', 'author')
    )
    context = {
        'page_obj': paginator(post_list, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Передаёт в шаблон posts/group_list.html
    десять последних объектов модели Post.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = (group.posts.select_related(
        'group',
        'author'
    ))
    context = {
        'group': group,
        'page_obj': paginator(posts, request)
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """"страница для отображения данных об авторе"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    context = {
        'page_obj': paginator(post_list, request),
        'author': author,
        'count_of_posts': post_list.count
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """"страница для отображения подробной информации о посте"""
    one_post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': one_post,
        'count_of_posts': one_post.author.posts.all().count(),
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """"создание новой записи (поста)."""
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """"позволяет редактировать имеющийся пост."""
    one_post = get_object_or_404(Post, pk=post_id)
    if request.user != one_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=one_post
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """позволяет добавлять комментарии"""
    post = get_object_or_404(Post.objects.filter(id=post_id))
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {'page_obj': paginator(posts, request)}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """подписка на автора"""
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_exist = Follow.objects.filter(
        user=request.user,
        author=author,
    ).exists()
    if not request.user == author and not follow_exist:
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """отписка от автора"""
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
