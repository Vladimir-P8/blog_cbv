from django import forms
from .models import Post, Comment
from ckeditor.widgets import CKEditorWidget

class PostCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    """

    title = forms.CharField(label='Заголовок', widget=CKEditorWidget(config_name='awesome_ckeditor'))

    class Meta:
        model = Post
        fields = ('title', 'category', 'description', 'text', 'thumbnail', 'tags', 'status')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

class PostUpdateForm(PostCreateForm):
    """
    Форма обновления статьи на сайте
    """
    #title = forms.CharField(label='Заголовок', widget=CKEditorWidget(config_name='awesome_ckeditor'))

    class Meta:
        model = Post
        fields = PostCreateForm.Meta.fields + ('updater', 'fixed')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)

        self.fields['fixed'].widget.attrs.update({
            'class': 'form-check-input'
        })


class CommentCreateForm(forms.ModelForm):
    """
    Форма добавления комментариев к статьям
    """
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(
        attrs={'cols': 30, 'rows': 5, 'placeholder': 'Комментарий', 'class': 'form-control'}))

    class Meta:
        model = Comment
        fields = ('content',)


class EmailPostForm(forms.Form):
    """Отправим рекомендуемый пост по Email"""
    name = forms.CharField(max_length=25, required=True, label='Имя',
                           widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'Введите обращение в письме..'}))
    email = forms.EmailField(required=True, label='E-mail, от кого',
                             widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'E-Mail отправителя...'}))
    to = forms.EmailField(required=True, label='E-mail, кому',
                          widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'E-Mail отправителя...'}))
    comments = forms.CharField(required=False, label='Комментарий',
                               widget=forms.Textarea(attrs={"class": "form-control mb-1", 'placeholder': 'Комментарий'}))

class SearchForm(forms.Form):
    """Форма поиска"""
    query = forms.CharField(label='Поиск',
                            widget=forms.TextInput(attrs={"class": "form-control mb-1", 'placeholder': 'Что ищем...'}))