from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

USER_MODEL = get_user_model()

AUTHOR = 'Автор'
USER = 'Пользователь'

SLUG = 'slug'

FIELD_NAMES = ('title', 'text', 'slug', 'author')
FIELD_DATA = ('Заголовок', 'Текст заметки', SLUG)

HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
DETAIL_URL = reverse('notes:detail', args=(SLUG,))


class TestAvailability(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = USER_MODEL.objects.create(username=AUTHOR)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = USER_MODEL.objects.create(username=USER)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            **dict(zip(FIELD_NAMES, (*FIELD_DATA, cls.author)))
        )

    def test_availability_for_users(self):
        urls = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (EDIT_URL, self.author_client, HTTPStatus.OK),
            (DELETE_URL, self.author_client, HTTPStatus.OK),
            (DETAIL_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.user_client, HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.user_client, HTTPStatus.NOT_FOUND),
            (DETAIL_URL, self.user_client, HTTPStatus.NOT_FOUND),
            (ADD_URL, self.user_client, HTTPStatus.OK),
            (SUCCESS_URL, self.user_client, HTTPStatus.OK),
            (LIST_URL, self.user_client, HTTPStatus.OK),
        )
        for url, client, expected_status in urls:
            with self.subTest(url=url):
                response = client.get(url).status_code
                self.assertEqual(
                    response,
                    expected_status,
                )

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for url in (
            LIST_URL,
            SUCCESS_URL,
            DELETE_URL,
            ADD_URL,
            EDIT_URL,
        ):
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
