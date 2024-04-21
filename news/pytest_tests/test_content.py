import pytest

from django.urls import reverse

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Количество новостей на странице."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    """Порядок сортировки новостей."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(comments, client, kwarg_news):
    """Порядок сортировки комментариев."""
    detail_url = reverse('news:detail', kwargs=kwarg_news)
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, kwarg_news):
    """Анонимный клиент не видит формы."""
    detail_url = reverse('news:detail', kwargs=kwarg_news)
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, kwarg_news):
    """Авторизованному клинту доступны формы."""
    detail_url = reverse('news:detail', kwargs=kwarg_news)
    response = author_client.get(detail_url)
    assert 'news' in response.context
    assert isinstance(response.context['form'], CommentForm)
