from django.views.generic import View, CreateView, ListView, DetailView, UpdateView, FormView
from .models import Post, Category,  Rating
from .forms import PostCreateForm, PostUpdateForm, EmailPostForm, \
    SearchForm, CommentCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from ..services.mixins import AuthorRequiredMixin
from django.http import JsonResponse
from django.utils.formats import date_format
from django.utils.timezone import localtime
from taggit.models import Tag
from django.shortcuts import render, redirect, get_object_or_404
# from django.db.models import Count # Для рекомендаций похожих постов
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank  # Для поиска
import logging
import nh3

# ---------------ЛОГГИРОВАНИЕ--------------------

logger = logging.getLogger(__name__)


# ---------------ОБРАБОТКА ОШИБОК--------------------

def tr_handler404(request, exception):
    """
    Обработка ошибки 404
    """
    return render(request=request, template_name='errors/error_page.html', status=404, context={
        'title': 'Страница не найдена: 404',
        'error_message': 'К сожалению такая страница была не найдена, или перемещена',
    })


def tr_handler500(request):
    """
    Обработка ошибки 500
    """
    return render(request=request, template_name='errors/error_page.html', status=500, context={
        'title': 'Ошибка сервера: 500',
        'error_message': 'Внутренняя ошибка сайта, вернитесь на главную страницу, отчёт об ошибке мы направим администрации сайта',
    })


def tr_handler403(request, exception):
    """
    Обработка ошибки 403
    """
    return render(request=request, template_name='errors/error_page.html', status=403, context={
        'title': 'Ошибка доступа: 403',
        'error_message': 'Доступ к этой странице ограничен',
    })

# ---------------ПОСТЫ--------------------
class PostByTagListView(ListView):
    """
    Представление материала на сайте, выведенного по тегу
    """
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = Post.objects.filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Статьи по тегу: {self.tag.name}'
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} отображает список по тегу')
        return super().get(request, *args, **kwargs)


class PostUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Представление: обновление материала на сайте
    """
    model = Post
    template_name = 'blog/post_update.html'
    context_object_name = 'post'
    form_class = PostUpdateForm
    # login_url = 'home'
    login_url = 'login'
    # success_message = 'Запись была успешно обновлена!'

    def get_success_message(self, cleaned_data):
        return f'Запись была успешно обновлена! <br> Автор обновления {self.request.user.username} '

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = set()
        context['title'] = f'Обновление статьи: {nh3.clean(self.object.title, tags=tags)}'
        # context['title'] = f'Обновление статьи: {self.object.title}'
        # context['slug'] = self.object.slug # new
        # context['slug']= self.kwargs.get('slug') # new
        # logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} получает контекст {context["slug"]}')
        return context

    def form_valid(self, form):
        form.instance.updater = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} редактирует пост')
        return super().get(request, *args, **kwargs)


class PostCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """
    Представление: создание материалов на сайте
    """
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostCreateForm
    login_url = 'login'

    def get_success_message(self, cleaned_data):
        # return f'Вы успешно зарегистрировались, <b>{self.request.user.username}</b>.<br>Можете войти на сайт!'
        return f'Пост успешно добавлен! <br>Автор <b>{self.request.user.username}</b>'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление статьи на сайт'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} создаёт пост')
        return super().get(request, *args, **kwargs)


class PostListView(ListView):
    # Определяем модель, данные из которой будут отображаться в представлении. Django автоматически получит все объекты модели
    # model = Post
    # Указывает путь к файлу шаблона относительно папки templates нашего Django проекта
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    queryset = Post.custom.all()  # Меняем менеджер на custom

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} открыл список постов')
        return super().get(request, *args, **kwargs)


class PostDetailView(DetailView):
    """
    Представление для отображения индивидуального поста
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # tags = nh3.ALLOWED_TAGS - {'p', 'span'}
        # tags = nh3.ALLOWED_TAGS - set()
        # print("До очистки", self.object.title)
        tags = set()
        context['title'] = nh3.clean(self.object.title, tags=tags)
        # print("После очистки", context['title'])
        # context['title'] = self.object.title.replace('<p>', '').replace('</p>', '').replace('<span style="font-family:Courier New,Courier,monospace">', '').replace('</span>','')
        # context['title'] = clean_title
        context['form'] = CommentCreateForm  # new
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} открыл детальное описание поста')
        return super().get(request, *args, **kwargs)


class PostFromCategory(ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    category = None
    paginate_by = 5

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        # queryset = Post.objects.filter(category=self.category)
        # queryset = Post.objects.filter(category__slug=self.category.slug)
        queryset = Post.custom.filter(category__slug=self.category.slug)  # Меняем менеджер на custom
        if not queryset:
            sub_cat = Category.objects.filter(parent=self.category)
            # queryset = Post.objects.filter(category__in=sub_cat)
            queryset = Post.custom.filter(category__in=sub_cat)  # Меняем менеджер на custom
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Записи из категории: {self.category.title}'
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} зашёл в список постов по категории')
        return super().get(request, *args, **kwargs)


class PostShare(FormView):
    """
    Представление для отправки рекомендаций по электронной почте
    """
    template_name = 'blog/share.html'
    form_class = EmailPostForm

    # Метод dispatch выполняется ДО get и post, здесь удобно получить пост
    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post,
                                          id=kwargs['post_id'],
                                          status='published')
        return super().dispatch(request, *args, **kwargs)

    # Передаем объект поста в контекст шаблона для GET и POST
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        return context

    # Вызывается автоматически, если форма валидна (заменяет if form.is_valid())
    def form_valid(self, form):
        cd = form.cleaned_data
        post_url = self.request.build_absolute_uri(self.post_obj.get_absolute_url())

        subject = f"{cd['name']} рекомендовал прочитать публикацию " \
                  f"\"{self.post_obj.title.replace('<p>', '').replace('</p>', '')}\""

        message = f"<p>Прочитайте публикацию \"{self.post_obj.title.replace('<p>', '').replace('</p>', '')}\", расположенную по <a href=\"{post_url}\">адресу</a>." \
                  f"<br> {cd['name']} с <a href=mailto:\"{cd['email']}\">электронной почты</a> оставил комментарий для вас: <br> \"{cd['comments']}\"</p>"

        # Отправить электронное письмо
        send_mail(
            subject, '',
            settings.EMAIL_HOST_USER, [cd['to']],
            html_message=message
        )

        messages.success(self.request, 'Сообщение успешно отправлено')
        return redirect(self.post_obj.get_absolute_url())

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} решил поделиться постом')
        return super().get(request, *args, **kwargs)


# def post_share(request, post_id):
#     """Представление для отправки рекомендаций по электронной почте
#     После проверки заменим на класс"""
#     # Извлечь пост по идентификатору id
#     # post = get_object_or_404(Post,
#     #                          id=post_id,
#     #                          status=Post.Status.PUBLISHED)
#     post = get_object_or_404(Post,
#                              id=post_id,
#                              status='published')
#     sent = False
#
#     if request.method == 'POST':
#         # Форма была передана на обработку
#         form = EmailPostForm(request.POST)
#         if form.is_valid():
#             # Поля формы успешно прошли валидацию
#             cd = form.cleaned_data
#             post_url = request.build_absolute_uri(
#                 post.get_absolute_url())
#             subject = f"{cd['name']} рекомендовал прочитать публикацию " \
#                       f"\"{post.title.replace('<p>', '').replace('</p>', '')}\""
#             # message = f"Прочитайте публикацию \"{post.title}<p>\", <br> расположенную по адресу {post_url}<br>" \
#             #           f"<br> {cd['name']} <br> с электронной почты ({cd['email']})<br> оставил комментарий для вас: <br> {cd['comments']}</p>"
#             message = f"<p>Прочитайте публикацию \"{post.title.replace('<p>', '').replace('</p>', '')}\", расположенную по <a href=\"{post_url}\">адресу</a>." \
#                       f"<br> {cd['name']} с <a href=mailto:\"{cd['email']}\">электронной почты</a> оставил комментарий для вас: <br> \"{cd['comments']}\"</p>"
#             # ... отправить электронное письмо
#             # send_mail(subject, message, settings.EMAIL_HOST_USER,
#                       # [cd['to']])
#             # send_mail(subject, message,
#             #           from_email=settings.EMAIL_HOST_USER,
#             #           recipient_list=[cd['to']],
#             #           html_message=message)
#             print(f'message={message}')
#             send_mail(subject,
#                       '',
#                       settings.EMAIL_HOST_USER, [cd['to']],
#                       html_message=message)
#
#             sent = True
#             messages.success(request, 'Сообщение успешно отправлено')
#
#             return redirect(post.get_absolute_url())
#             # comment.post.get_absolute_url()
#
#     else:
#         form = EmailPostForm()
#     return render(request, 'blog/share.html', {'post': post,
#                                                     'form': form})

class PostSearchView(FormView):
    form_class = SearchForm
    template_name = 'blog/search.html'

    # Переопределяем, чтобы форма брала данные из GET, а не из POST
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'query' in self.request.GET:
            kwargs['data'] = self.request.GET
        return kwargs

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        query = None
        results = []

        if form.is_valid():
            query = form.cleaned_data['query']

            search_vector = (
                    SearchVector('title', 'description', 'text', config='my_russian_conf') +
                    SearchVector('title', 'description', 'text', config='english')
            )

            search_query = (
                    SearchQuery(query, config='my_russian_conf') |
                    SearchQuery(query, config='english')
            )

            results = Post.custom.all().annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')

        context = self.get_context_data(
            form=form,
            query=query,
            results=results
        )
        return self.render_to_response(context)

    # Обрабатываем GET-запрос вместо POST
    # def get(self, request, *args, **kwargs):
    #     form = self.get_form()
    #     query = None
    #     results = []
    #
    #     if form.is_valid():
    #         query = form.cleaned_data['query']
    #
    #         search_vector = (
    #                 SearchVector('title', weight='A', config='my_russian_conf') +
    #                 SearchVector('text', weight='B', config='my_russian_conf') +
    #                 SearchVector('title', weight='A', config='english') +
    #                 SearchVector('text', weight='B', config='english')
    #         )
    #         # search_vector = SearchVector('title', 'text', config='russian')
    #         # search_vector = SearchVector('title', weight='A') + \
    #         #                 SearchVector('text', weight='B')
    #         search_query = (
    #                 SearchQuery(query, config='my_russian_conf') |
    #                 SearchQuery(query, config='english')
    #         )
    #         # search_query = SearchQuery(query, config='my_russian_conf')
    #
    #         results = Post.custom.all().annotate(
    #             search=search_vector,
    #             rank=SearchRank(search_vector, search_query)
    #         ).filter(search=search_query).order_by('-rank')
    #
    #     context = self.get_context_data(
    #         form=form,
    #         query=query,
    #         results=results
    #     )
    #     logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} ищет {query}')
    #     return self.render_to_response(context)


# ---------------КОММЕНТАРИИ--------------------
class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': date_format(
                    localtime(comment.time_create),
                    format='DATETIME_FORMAT',
                    use_l10n=True,
                ),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)

        return redirect(comment.post.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} создаёт комментарий')
        return super().get(request, *args, **kwargs)


# ---------------РЕЙТИНГ--------------------
class RatingCreateView(View):
    model = Rating

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        value = int(request.POST.get('value'))
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user = request.user if request.user.is_authenticated else None

        rating, created = self.model.objects.get_or_create(
            post_id=post_id,
            ip_address=ip,
            defaults={'value': value, 'user': user},
            )

        if not created:
            if rating.value == value:
                rating.delete()
            else:
                rating.value = value
                rating.user = user
                rating.save()
        return JsonResponse({'rating_sum': rating.post.get_sum_rating()})

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} создаёт рейтинг')
        return super().get(request, *args, **kwargs)
