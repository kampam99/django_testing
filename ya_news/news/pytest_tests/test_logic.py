from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client,
                                            form_data,
                                            news,
                                            url_detail):
    before_update_count = Comment.objects.count()
    client.post(url_detail, data=form_data)
    assert before_update_count == Comment.objects.count()


def test_user_can_create_comment(author_client,
                                 author,
                                 form_data,
                                 news,
                                 url_detail):
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, url_detail):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url_detail, data=bad_words_data)
    assertFormError(
        response,
        'form',
        'text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client,
                                 form_data,
                                 comment,
                                 news,
                                 author,
                                 url_detail
                                 ):
    response = author_client.post(url_detail, form_data)
    assertRedirects(response, f'{url_detail}#comments')
    news.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author


def test_author_can_delete_comment(author_client,
                                   comment,
                                   news,
                                   url_delete,
                                   url_detail):
    before_update_count = Comment.objects.count()
    response = author_client.delete(url_delete)
    assertRedirects(response, url_detail + '#comments')
    assert before_update_count != Comment.objects.count()


def test_user_cant_delete_comment_of_another_user(admin_client,
                                                  comment,
                                                  url_delete):
    before_update_count = Comment.objects.count()
    response = admin_client.delete(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert before_update_count == Comment.objects.count()


def test_other_user_cant_delete_note(admin_client,
                                     form_data,
                                     url_delete):
    before_update_count = Comment.objects.count()
    response = admin_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert before_update_count == Comment.objects.count()
