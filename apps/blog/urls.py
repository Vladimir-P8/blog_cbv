from django.urls import path
from .views import PostListView, PostDetailView, \
    PostFromCategory,  PostCreateView, PostUpdateView, \
    CommentCreateView, PostByTagListView, RatingCreateView,\
    PostShare, PostSearchView


urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),  # New
    path('post/tags/<str:tag>/', PostByTagListView.as_view(), name='post_by_tags'),  # New
    path('category/<slug:slug>/', PostFromCategory.as_view(), name="post_by_category"),
    path('rating/', RatingCreateView.as_view(), name='rating'),  # New
    # path('<int:post_id>/share/',post_share, name='post_share'),
    path('<int:post_id>/share/', PostShare.as_view(), name='post_share'),  # New
    # path('search/', views.post_search, name='post_search'),
    path('search/', PostSearchView.as_view(), name='post_search'),


]
