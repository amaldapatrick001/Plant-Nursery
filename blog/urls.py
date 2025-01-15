# blog/urls.py

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('dashboard/', views.blog_dashboard, name='dashboard'),
    path('add/', views.add_blog_post, name='add'),
    path('edit/<int:post_id>/', views.edit_blog_post, name='edit'),
    path('delete/<int:post_id>/', views.delete_blog_post, name='delete'),
    path('home/', views.blog_home, name='home'),
    path('detail/<int:post_id>/', views.blog_detail, name='detail'),
path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('like/', views.like_blog_post, name='like_blog_post'),
]