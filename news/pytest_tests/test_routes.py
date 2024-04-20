import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('kwarg_news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, kwargs):
    """
    Доступность главной страницы, входа, выхода, регистрации,
    отдельной новости.
    """
    url = reverse(name, kwargs=kwargs)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
        'user_client, status_code',
        (
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        )
)
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:edit', pytest.lazy_fixture('kwarg_comment')),
        ('news:delete', pytest.lazy_fixture('kwarg_comment'))
    ),
)
def test_availability_for_comment_edit_and_delete(
    name, kwargs, user_client, status_code
     ):
    """
    Доступность страниц изменеия/удаления комментария
    для автора и другого пользователя.
    """
    url = reverse(name, kwargs=kwargs)
    response = user_client.get(url)
    assert response.status_code == status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:edit', pytest.lazy_fixture('kwarg_comment')),
        ('news:delete', pytest.lazy_fixture('kwarg_comment'))
    ),
)
def test_redirect_for_anonymous_client(client, name, kwargs):
    """Перенаправление для незарегистрированных пользователей."""
    login_url = reverse('users:login')
    url = reverse(name, kwargs=kwargs)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
