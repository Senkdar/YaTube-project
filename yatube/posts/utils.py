from django.core.paginator import Paginator


COUNT_OF_POSTS: int = 10


def paginator(queryset, request):
    """функция для постраничного деления контента"""
    paginator = Paginator(queryset, COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
