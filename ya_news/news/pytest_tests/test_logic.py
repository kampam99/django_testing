from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import DELETE_URL, EDIT_URL, DETAIL_URL

NEW_COMMENT_TEXT = 'Новый текст комментария'


@pytest.mark.django_db
def test_noname_user_cant_create_comment(
        client, form_data, news_id_for_args):
    assert Comment.objects.count() == 0
    client.post(DETAIL_URL, data=form_data)
    assert Comment.objects.count() == 0


def test_comment_creation(author_client, author, form_data, news):
    response = author_client.post(DETAIL_URL, data=form_data)
    assertRedirects(response, f'{DETAIL_URL}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news is not news.title


def test_user_cant_use_bad_words(author_client, form_data, news_id_for_args):
    form_data['text'] = f'Текст, {BAD_WORDS[0]}, текст, вторая часть'
    assert Comment.objects.count() == 0
    response = author_client.post(DETAIL_URL, data=form_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_the_author_granded_to_edit_comment(
        author_client, form_data,
        comment, news_id_for_args,
        comment_id_for_args, author):
    url_to_comments = DETAIL_URL + '#comments'
    response = author_client.post(EDIT_URL, form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == form_data['text']
    assert comment.text == comment_from_db.text
    assert comment.author == author
    assert comment.created == comment_from_db.created
    assert comment.news == comment_from_db.news


def test_noname_user_cant_edit_comment(admin_client,
                                       form_data,
                                       comment,
                                       comment_id_for_args,
                                       author):
    response = admin_client.post(EDIT_URL, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == author
    assert comment.created == comment_from_db.created
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(
        author_client, news_id_for_args, comment_id_for_args):
    url_to_comments = DETAIL_URL + '#comments'
    assert Comment.objects.count() == 1
    response = author_client.delete(DELETE_URL)
    assertRedirects(response, url_to_comments)
    assert response != url_to_comments
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        admin_client, comment_id_for_args):
    assert Comment.objects.count() == 1
    response = admin_client.post(DELETE_URL)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
