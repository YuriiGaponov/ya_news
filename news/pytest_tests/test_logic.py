import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, comment_form, kwarg_news):
    """Анонимный полльзователь не может создавать комментарий."""
    url = reverse('news:edit', kwargs=kwarg_news)
    client.post(url, data=comment_form)
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_user_can_create_comment(
        author_client, comment_form, url_comment_edit,
        kwarg_comment, news, author
     ):
    """Авторизованный пользователь может создавать комментарии."""
    author_client.post(url_comment_edit, data=comment_form)
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
@pytest.mark.usefixtures('author', 'kwarg_comment')
def test_user_cant_use_bad_words(
        author_client, bad_words_form, url_comment_edit,
     ):
    """Пользователь не может использовать в комментах запрещенные слова."""
    response = author_client.post(url_comment_edit, data=bad_words_form)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comment_count = Comment.objects.count()
    assert comment_count == 1


@pytest.mark.django_db
@pytest.mark.usefixtures('kwarg_comment', 'news')
def test_author_can_delete_comment(
    author_client, url_comment_delete, news_url
     ):
    """Авторизованный пользователь может удалять свои комментарии."""
    url_to_comments = news_url + '#comments'
    response = author_client.delete(url_comment_delete)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment_of_another_user(
    reader_client, url_comment_delete
     ):
    """Пользователь не может удалять чужие комментарии."""
    response = reader_client.delete(url_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
@pytest.mark.usefixtures('news')
def test_author_can_edit_comment(
    author_client, comment, comment_form, news_url, url_comment_edit
     ):
    """Автор может редактировать свои комменты."""
    response = author_client.post(url_comment_edit, data=comment_form)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_form['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, comment_form, url_comment_edit
     ):
    """Пользователь не может редактировать чужие комменты."""
    comment_text = comment.text
    response = reader_client.post(url_comment_edit, data=comment_form)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
