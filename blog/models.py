from django.db import models
from userauths.models import Login, User_Reg, DeliveryPersonnel

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    images = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    videos = models.FileField(upload_to='blog_videos/', blank=True, null=True)
    author = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    like_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def soft_delete(self):
        """Soft delete the blog post"""
        self.is_deleted = True
        self.save()

    def restore(self):
        """Restore the soft-deleted blog post"""
        self.is_deleted = False
        self.save()


class BlogPostLike(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.fname} on {self.post.title}"

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    comment = models.TextField()
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.post.title}"

class BlogBookmark(models.Model):
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmark by {self.user.username} for {self.post.title}"
