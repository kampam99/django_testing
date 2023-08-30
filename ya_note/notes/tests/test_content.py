from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.notes = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст комментария',
            slug='123'
        )
        cls.other_auth_client = Client()
        cls.other_auth_client.force_login(cls.reader)

    def test_notes_sent(self):
        response = self.auth_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.other_auth_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_create_note_page_contains_form(self):
        response = self.auth_client.get(self.ADD_URL)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_client.get(url)
        self.assertIn('form', response.context)
