import pytest
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from pytest_lazyfixture import lazy_fixture

from news.models import News, Comment

PK = 1
COMMENT_TEXT = 'Комментарий'
NEW_COMMENT_TEXT = 'Новый текст комментария'
ADMIN = lazy_fixture('admin_client')
AUTHOR = lazy_fixture('author_client')
CLIENT = lazy_fixture('client')


HOME_URL = reverse('news:home')
DETAIL_URL = reverse('news:detail', args=(PK,))
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
EDIT_URL = reverse('news:edit', args=(PK,))
DELETE_URL = reverse('news:delete', args=(PK,))


@pytest.fixture
def urls(parametrized_client):
    urls = reverse('news:home')
    return urls


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    note = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return note


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def news_pk(news):
    return news.pk,


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def news_objects():
    today = datetime.today()

    all_news = [
        News(
            title=f'Новость {index}',
            text='Tекст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    News.objects.bulk_create(all_news)


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    created_comments = []

    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        created_comments.append(comment)

    return created_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }
