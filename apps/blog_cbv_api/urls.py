from django.urls import path
from .views import PostList, PostDetail, UserPostList
from drf_spectacular.views import SpectacularAPIView, \
    SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('', PostList.as_view(), name='post_list'),
    path('user/<int:id>/', UserPostList.as_view()),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # new
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # new
]