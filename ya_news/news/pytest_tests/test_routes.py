import pytest

from django.urls import reverse
from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from news.pytest_tests.conftest import (ADMIN, AUTHOR, CLIENT,
                                        HOME_URL, DETAIL_URL,
                                        LOGIN_URL, LOGOUT_URL, SIGNUP_URL,
                                        EDIT_URL, DELETE_URL)


@pytest.mark.parametrize(
    'url, parametrized_client, status',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR, HTTPStatus.OK),
        (DELETE_URL, AUTHOR, HTTPStatus.OK),
        (EDIT_URL, ADMIN, HTTPStatus.NOT_FOUND),
        (DELETE_URL, ADMIN, HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(
        url, parametrized_client, status, comment):
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
