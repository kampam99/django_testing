from notes.forms import NoteForm
from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

AUTHOR = 'Автор'
SLUG = 'note-slug'
USER = 'Пользователь'
USER_MODEL = get_user_model()
FIELD_NAMES = ('title', 'text', 'slug', 'author')
FIELD_DATA = ('Заголовок', 'Текст заметки', SLUG)
FIELD_NEW_DATA = ('Новый заголовок', 'Новый текст', 'new-slug')
ADD_URL = reverse('notes:add')
NOTES_LIST_URL = reverse('notes:list')


URL_NAME = namedtuple(
    'NAME',
    [
        'home',
        'add',
        'list',
        'detail',
        'edit',
        'delete',
        'success',
        'login',
        'logout',
        'signup',
    ],
)


class SetUpTestCase(TestCase):
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


class TestNoteList(SetUpTestCase):
    def test_list_context(self):
        clients = (
            (self.author_client, True),
            (self.user_client, False),
        )
        for client, value in clients:
            with self.subTest(client=client):
                content_objects = client.get(
                    NOTES_LIST_URL).context['object_list']
                self.assertTrue((self.note in content_objects) is value)

    def test_form_context(self):
        with self.subTest(url=ADD_URL):
            self.assertIsInstance(
                self.author_client.get(ADD_URL).context['form'], NoteForm,)
