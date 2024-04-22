import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(
        username='Пользователь'
    )


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(
        username='Другой пользователь'
    )


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст'
    )


@pytest.fixture
def kwarg_news(news):
    return {'pk': news.pk}


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )


@pytest.fixture
def kwarg_comment(comment):
    return {'pk': comment.pk}


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'Текст комментария {index}',
            created=now + timedelta(days=index)
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
def comment_form():
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def bad_words_form():
    return {
        'text': f'Коммент с недопустимым словом {BAD_WORDS[0]}'
        }


@pytest.fixture
def url_comment_edit(kwarg_news):
    return reverse('news:edit', kwargs=kwarg_news)


@pytest.fixture
def url_comment_delete(kwarg_comment):
    return reverse('news:delete', kwargs=kwarg_comment)
