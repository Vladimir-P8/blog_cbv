"""
URL configuration for blog_cbv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from apps.blog.feeds import LatestPostFeed
from django.contrib.sitemaps.views import sitemap # Карта сайта
from apps.blog.sitemaps import PostSitemap # Карта сайта

sitemaps = {
    'posts': PostSitemap,
}


handler403 = 'apps.blog.views.tr_handler403' # Обработчик ошибки
handler404 = 'apps.blog.views.tr_handler404' # Обработчик ошибки
handler500 = 'apps.blog.views.tr_handler500' # Обработчик ошибки


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')), #'apps.accounts.urls' должны быть первее 'django.contrib.auth.urls'
    path('', include('apps.blog.urls')),
    # path('accounts/', include('apps.accounts.urls')),
    path('', include('django.contrib.auth.urls')),

    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('feeds/latest/', LatestPostFeed(), name='latest_post_feed'),  # New
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'), # Карта сайта
    path('oauth/', include('social_django.urls', namespace='social')),
    path('api/', include('apps.blog_cbv_api.urls')),
    path('api-auth/', include('rest_framework.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()



    # urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

