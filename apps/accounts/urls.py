from django.urls import path, include
from .views import ProfileUpdateView, ProfileDetailView, UserRegisterView, UserLoginView, UserLogoutView
from django.views.generic import TemplateView


urlpatterns = [
    path('user/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('user/<slug:slug>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # path('accounts/', include('django.contrib.auth.urls')),
path('privacy/', TemplateView.as_view(template_name='documents/privacy.html'), name='privacy_policy'),
    path('agreement/',  TemplateView.as_view(template_name='documents/agreement.html'), name='user_agreement'),

]

