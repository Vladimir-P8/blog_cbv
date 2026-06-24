from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django_filters.rest_framework import DjangoFilterBackend  # new
from rest_framework import generics, permissions
from apps.blog.models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly  # new
import logging

# ---------------ЛОГГИРОВАНИЕ--------------------

logger = logging.getLogger(__name__)

# class PostList(APIView):
class PostList(generics.ListCreateAPIView):
    name = "Список публикаций"
    permission_classes = (IsAuthorOrReadOnly,)  # new
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]  # new
    filterset_fields = ['author']  # new

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} отображает список постов в API')
        return super().get(request, *args, **kwargs)

    # def get_queryset(self):
    #     user = self.request.user
    #     return Post.objects.filter(author=user)

    # def get(self, request, format=None):
    #     posts = Post.objects.all()
    #     serializer = PostSerializer(posts, many=True)
    #     return Response(serializer.data)
    #
    # def post(self, request, format=None):
    #     serializer = PostSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data,
    #                         status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PostDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Post.objects.get(pk=pk)
#         except Post.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         post = self.get_object(pk)
#         serializer = PostSerializer(post)
#         return Response(serializer.data)
#
#     def put(self, request, pk, format=None):
#         post = self.get_object(pk)
#         serializer = PostSerializer(post, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def patch(self, request, pk, format=None):
#         post = self.get_object(pk)
#         serializer = PostSerializer(post,
#                                     data=request.data,
#                                     partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         post = self.get_object(pk)
#         post.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    name = "Детали публикации"
    permission_classes = (IsAuthorOrReadOnly,)  # new
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} смотрит детальное описание поста в API')
        return super().get(request, *args, **kwargs)

    # permission_classes = (permissions.IsAdminUser,)  # new
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # def get_queryset(self):
    #     queryset = Post.objects.all()
    #     # user = self.request.user
    #     return queryset

class UserPostList(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.kwargs['id']
        return Post.objects.filter(author=user)

    def get(self, request, *args, **kwargs):
        logger.info(f'{self.__class__.__name__}: Пользователь {self.request.user} отображает список своих постов в API')
        return super().get(request, *args, **kwargs)