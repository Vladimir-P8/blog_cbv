from django import template
from ..models import Post
from django.db.models import Count, Sum
import nh3

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.custom.count()


@register.inclusion_tag('blog/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.custom.order_by('-create')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.custom.annotate(
        total_comments=Count('comments')
    ).exclude(total_comments=0).order_by('-total_comments')[:count]


@register.filter(name='safe_text')
def safe_text(text):
    # print(text)
    tags = set()
    clean_text = nh3.clean(text, tags=tags)
    # print(clean_text)
    return clean_text


@register.simple_tag
def get_high_rating_posts(count=5):
    return Post.custom.annotate(
        high_rating_posts=Sum('ratings__value', default=0)
    ).order_by('-high_rating_posts')[:count]