import pytest
from http import HTTPStatus
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm

from news.pytest_tests.conftest import DETAIL_URL, HOME_URL


@pytest.mark.django_db
def test_news_count(client, news_objects):
    response = client.get(HOME_URL)
    news_objects = response.context['object_list']
    news_count = len(news_objects)
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_objects):
    response = client.get(HOME_URL)
    news_objects = response.context['object_list']
    all_dates = [news.date for news in news_objects]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(client, comments, news_pk):
    url = DETAIL_URL
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    comments = list(response.context['object'].comment_set.all())
    sorted_comments = sorted(comments, key=lambda x: x.created)
    assert comments == sorted_comments


def test_pages_data_for_different_users(
        client, admin_client, news):
    response = client.get(DETAIL_URL)
    admin_response = admin_client.get(DETAIL_URL)
    assert (isinstance(admin_response.context['form'], CommentForm)
            and 'form' not in response.context)
