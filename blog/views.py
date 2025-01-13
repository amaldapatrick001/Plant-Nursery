
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import BlogComment, BlogPost
from .forms import BlogPostForm

def ensure_user_logged_in(request):
    """Ensure the user is logged in; if not, redirect to login with an error message."""
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to proceed.')
        return False
    return True

# Blog views with session handling

def blog_dashboard(request):
    """Render the dashboard of blog posts for the logged-in user."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    posts = BlogPost.objects.filter(author_id=request.session['user_id']).order_by('-created_at')
    return render(request, 'blog/dashboard.html', {'posts': posts})

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BlogPostForm

def add_blog_post(request):
    """Allow the logged-in user to add a new blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author_id = request.session['user_id']  # Set the author as the logged-in user
            blog_post.save()
            # Ensure `messages.success` is being used correctly
            messages.success(request, 'Blog post added successfully!')
            return redirect('blog:dashboard')
    else:
        form = BlogPostForm()

    return render(request, 'blog/add_post.html', {'form': form})

def edit_blog_post(request, post_id):
    """Allow the logged-in user to edit their own blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog:dashboard')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form})

def delete_blog_post(request, post_id):
    """Allow the logged-in user to delete their own blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
    post.delete()
    messages.success(request, 'Blog post deleted successfully!')
    return redirect('blog:dashboard')

def blog_home(request):
    """Render the public-facing blog homepage."""
    posts = BlogPost.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'blog/home.html', {'posts': posts})

def blog_detail(request, post_id):
    """Render the detailed view of a single blog post with comments."""
    post = get_object_or_404(BlogPost, id=post_id, is_public=True)
    comments = post.comments.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to leave a comment.')
            return redirect('userauths:login')

        comment_text = request.POST.get('comment')
        BlogComment.objects.create(post=post, user=request.user, comment=comment_text)
        messages.success(request, 'Comment added successfully!')
        return redirect('blog:detail', post_id=post_id)

    return render(request, 'blog/detail.html', {'post': post, 'comments': comments})


# Cart and checkout views with session handling (excluding add_to_cart function)

# Assuming there are more views to manage cart and checkout, but without the add_to_cart function:
# Other cart and checkout functions would use ensure_user_logged_in to check session before proceeding.
