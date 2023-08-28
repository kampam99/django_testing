from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'slug'

EDIT_URL = reverse('notes:edit', args=(SLUG,))
ADD_URL = reverse('notes:add')
DELETE_URL = reverse('notes:delete', args=(SLUG,))
SUCCESS_URL = reverse('notes:success')


class TestNotesCreation(TestCase):
    TEST_SLUG = "Slug_text"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = ADD_URL
        cls.form_data = {
            'title': 'Заголовок', 'text': 'Текст',
            'slug': cls.TEST_SLUG,
        }

    def test_note_creation(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_slug_automatically_creation(self):
        self.form_data['slug'] = ""
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.get()
        self.assertNotEqual(note.slug, '')

    def test_creation_couple_of_similar_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_counts_first_step = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_counts_second_step = Note.objects.count()
        self.assertEqual(notes_counts_first_step, notes_counts_second_step)


class TestNotesEditDelete(TestCase):
    ORIGINAL_TEXT = "Original"
    NEW_TEXT = "NewOne"

    @classmethod
    def setUpTestData(cls):
        cls.other = User.objects.create(username='otherUser')
        cls.author = User.objects.create(username='testUser')
        cls.note_author = Note.objects.create(
            title='Заголовок1', text=cls.ORIGINAL_TEXT,
            slug='slug', author=cls.author, )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.other)
        cls.edit_url = EDIT_URL
        cls.delete_url = DELETE_URL
        cls.redirect_url = SUCCESS_URL
        cls.form_data = {
            'title': 'Заголовок', 'text': cls.NEW_TEXT,
            'slug': 'qt', 'author': cls.author, }

    def test_deletion_restriction_foreign_notes(self):
        response = self.other_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_notes_deletion_with_right_permission(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)

    def test_editing_restriction_foreign_notes(self):
        response = self.other_client.post(self.edit_url,
                                          data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_author.refresh_from_db()
        self.assertEqual(self.note_author.text, self.ORIGINAL_TEXT)

    def test_editing_notes_with_right_permission(self):
        response = self.author_client.post(self.edit_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note_author.refresh_from_db()
        self.assertEqual(self.note_author.text, self.NEW_TEXT)
