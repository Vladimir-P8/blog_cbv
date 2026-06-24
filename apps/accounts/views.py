from django.views.generic import DetailView, UpdateView, CreateView
from django.db import transaction
from django.urls import reverse_lazy
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, UserLoginForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
import logging

# ---------------ЛОГГИРОВАНИЕ--------------------

logger = logging.getLogger(__name__)


# Нам нужен стандартный функционал
# Логин - есть - class UserLoginView(SuccessMessageMixin, LoginView):
# Логаут - есть - class UserLogoutView(LogoutView):
# Регистрация - есть - class UserRegisterView(SuccessMessageMixin, CreateView):
# Профиль - есть - class ProfileDetailView(DetailView):
# ПрофильОбновить - class ProfileUpdateView(UpdateView):
# Пароль сбросить - надо написать

# ---------------ЛОГИН--------------------
class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Авторизация пользователя на сайте
    """
    form_class = UserLoginForm
    template_name = 'accounts/user_login.html'
    next_page = 'home'

    def get_success_message(self, cleaned_data):
        return f'Добро пожаловать на сайт, <b>{self.request.user.username}</b>!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} заходит на сайт')
        return super().get(request, *args, **kwargs)

class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """
    next_page = 'home'

# ---------------РЕГИСТРАЦИЯ--------------------
class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """
    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/user_register.html'

    def get_success_message(self, cleaned_data):
        # return f'Вы успешно зарегистрировались, <b>{self.request.user.username}</b>.<br>Можете войти на сайт!'
        return f'Вы успешно зарегистрировались, <b>{cleaned_data["username"]}</b>.<br>Можете войти на сайт!'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} регистрируется на сайте')
        return super().get(request, *args, **kwargs)


# ---------------ПРОФИЛЬ--------------------
class ProfileDetailView(DetailView):
    """
    Представление для просмотра профиля
    """
    model = Profile
    context_object_name = 'profile'
    template_name = 'accounts/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Профиль пользователя: {self.object.user.username}'
        return context

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} смотрит свой профиль')
        return super().get(request, *args, **kwargs)


class ProfileUpdateView(UpdateView):
    """
    Представление для редактирования профиля
    """
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                return self.render_to_response(context)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'slug': self.object.slug})

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} обновляет профиль')
        return super().get(request, *args, **kwargs)

# ---------------ПАРОЛЬ--------------------

