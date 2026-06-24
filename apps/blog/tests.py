from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.blog.models import Post, Comment, Category
from django.db.models.signals import post_save
from apps.accounts.signals import create_user_profile # путь к вашей функции-сигналу
import logging
# Чтобы не печатались во множестве Traceback (most recent call last):
# надо добавить строку sys.tracebacklimit = 0
import sys
sys.tracebacklimit = 0

logger = logging.getLogger('django.request')

User = get_user_model()

# Tests run in alphabetical order
class BaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # print('Отключаем сигнал перед загрузкой фикстур класса')
        post_save.disconnect(create_user_profile, sender=User)
        super().setUpClass()

    fixtures = ['data3.json']

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # print('Включаем обратно сигнал после загрузки фикстур класса')
        post_save.connect(create_user_profile, sender=User)


class PostSlugTests(BaseTest):
    """
    Проверка детального отображения индивидуального поста на основе PostDetailView.as_view().
    """
    def test_url_access(self):
        # path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
        url = '/post/pervaya-testovaya-statya/'
        response = self.client.get(url)
        # print("ОТВЕТ 1:", response.status_code)
        self.assertEqual(response.status_code, 200)


class PostTagsTagTests(BaseTest):
    """
    Проверка отображения списка постов по тегу на основе PostByTagListView.as_view()
    """
    def test_url_access(self):
        # path('post/tags/<str:tag>/', PostByTagListView.as_view(), name='post_by_tags'),  # New
        url = '/post/tags/django/'
        response = self.client.get(url)
        # print("ОТВЕТ 2:", response.status_code)
        self.assertEqual(response.status_code, 200)


class HomePageGetTests(BaseTest):
    """
    Проверка стартовой страницы.
    """

    def test_url_access(self):
        # path('', PostListView.as_view(), name='home'),
        url = '/'
        response = self.client.get(url)
        # print("ОТВЕТ 3:", response.status_code)
        self.assertEqual(response.status_code, 200)


class PostCreateTests(BaseTest):
    """
    Проверка создания поста на основе PostCreateView.as_view().
    """

    def test_user_url_access(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        # path('post/create/', PostCreateView.as_view(), name='post_create'),
        url = '/post/create/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonim_url_access(self):
        # path('post/create/', PostCreateView.as_view(), name='post_create'),
        url = '/post/create/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class PostSlugUpdateTests(BaseTest):
    """
    Проверка обновления поста на основе PostUpdateView.as_view().
    """
    def test_user_url_access(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        # path('post/<slug:slug>/update/', PostUpdateView.as_view(), name='post_update'),
        url = '/post/pervaya-testovaya-statya/update/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonim_url_access(self):
        # path('post/<slug:slug>/update/', PostUpdateView.as_view(), name='post_update'),
        url = '/post/pervaya-testovaya-statya/update/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class PostPkCommentsCreateTests(BaseTest):
    """
    Проверка комментария на основе CommentCreateView.as_view().
    """
    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.post = Post.objects.first()
        self.url = reverse('comment_create_view', kwargs={'pk': self.post.pk})


    def test_anonim_create_comment(self):
        logger.disabled = True
        comments_count = Comment.objects.count()
        response = self.client.post(self.url, {'content': 'Test comment'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), comments_count)


    def test_anonim_create_comment_ajax(self):
        logger.disabled = True
        comments_count = Comment.objects.count()
        response = self.client.post(self.url, {'content': 'Test comment'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), comments_count)


    def test_user_create_comment(self):
        self.client.force_login(self.user)

        comments_count = Comment.objects.count()
        response = self.client.post(self.url, {'content': 'Test comment'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), comments_count + 1)


    def test_user_create_comment_ajax(self):
        self.client.force_login(self.user)
        comments_count = Comment.objects.count()

        response = self.client.post(self.url, {'content': 'Ajax comment'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

        data = response.json()

        self.assertEqual(data['author'], self.user.username)
        self.assertEqual(data['content'], 'Ajax comment')
        self.assertFalse(data['is_child'])


    def test_user_create_comment_invalid_ajax(self):
        logger.disabled = True
        self.client.force_login(self.user)
        comments_count = Comment.objects.count()

        response = self.client.post(self.url, {'content': ''}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), comments_count)

        data = response.json()
        self.assertIn('error', data)


    def test_user_create_child_comment_ajax(self):
        self.client.force_login(self.user)

        parent = Comment.objects.create(post=self.post, author=self.user, content='Parent comment')
        comments_count = Comment.objects.count()

        response = self.client.post(self.url, {'content': 'Child comment', 'parent': parent.pk},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

        data = response.json()

        self.assertEqual(data['author'], self.user.username)
        self.assertEqual(data['content'], 'Child comment')
        self.assertTrue(data['is_child'])

# Эти тесты содержат ошибки
    def test_user_url_access(self):
        logger.disabled = True
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        # path('post/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),
        url = '/post/1/comments/create/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonim_url_access(self):
        logger.disabled = True
        # path('post/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),
        url = '/post/1/comments/create/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)



class CategorySlugTests(BaseTest):
    """
    Проверка списка постов по категории на основе PostFromCategory.as_view().
    """
    def test_url_access(self):
        # path('category/<slug:slug>/', PostFromCategory.as_view(), name="post_by_category"),
        url = '/category/django/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# class RatingTests(BaseTest):
#     """
#     Проверка рейтинга постов на основе RatingCreateView.as_view().
#     """
#     def test_url_access(self):
#         # path('rating/', RatingCreateView.as_view(), name='rating'),
#         url = '/rating/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#
# class PostIdShareTests(TestCase):
#     def test_url_access(self):
#         url = '/<int:post_id>/share/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#
# class SearchTests(TestCase):
#     def test_url_access(self):
#         url = '/search/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#

