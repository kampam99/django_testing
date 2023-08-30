import pytest
from django.contrib.auth import get_user_model
from news.forms import CommentForm
User = get_user_model()

pytestmark = pytest.mark.django_db


def test_news_count(all_news, client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    assert len(object_list) == len(all_news)


def test_news_order(all_news, client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('created_comment')
def test_comments_order(client, url_detail):
    response = client.get(url_detail)
    object_list_comments = list(response.context['news'].comment_set.all())
    sorted_comments = sorted(
        object_list_comments, key=lambda comment: comment.created
    )
    assert object_list_comments == sorted_comments


def test_anonymous_client_has_no_form(news, client, url_detail):
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, url_detail):
    response = author_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
