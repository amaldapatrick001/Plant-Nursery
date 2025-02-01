# blog/urls.py

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('dashboard/', views.blog_dashboard, name='dashboard'),
    path('add/', views.add_blog_post, name='add'),
    path('eadd_blog/', views.eadd_blog, name='eadd_blog'),
    path('edit/<int:post_id>/', views.edit_blog_post, name='edit_blog_post'),
    path('eedit_blog_post/<int:post_id>/', views.eedit_blog_post, name='eedit_blog_post'),
    path('delete/<int:post_id>/', views.delete_blog_post, name='delete'),
    path('home/', views.blog_home, name='home'),
    path('detail/<int:post_id>/', views.blog_detail, name='detail'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('like/', views.like_blog_post, name='like_blog_post'),
    path('blog_dashboard/', views.blog_dashboard, name='blog_dashboard'),
    path('delete_blog_post/<int:post_id>/', views.delete_blog_post, name='delete_blog_post'),
    path('restore_blog_post/<int:post_id>/', views.restore_blog_post, name='restore_blog_post'),
    path('adelete_blog_post/<int:post_id>/', views.adelete_blog_post, name='adelete_blog_post'),
    path('arestore_blog_post/<int:post_id>/', views.arestore_blog_post, name='arestore_blog_post'),
    path('admin_blog_dashboard/', views.admin_blog_dashboard, name='admin_blog_dashboard'),
]