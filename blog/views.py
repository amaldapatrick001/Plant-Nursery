from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import BlogComment, BlogPost
from .forms import BlogPostForm
from userauths.models import Expert, Login

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

    posts = BlogPost.objects.filter(
        author_id=request.session['user_id']
    ).order_by('-created_at')
    
    return render(request, 'blog/blog_dashboard.html', {'posts': posts})

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
            blog_post.is_public = True
            blog_post.author_id = request.session['user_id']  # Set the author as the logged-in user
            blog_post.save()
            # Ensure `messages.success` is being used correctly
            messages.success(request, 'Blog post added successfully!')
            return redirect('blog:dashboard')
    else:
        form = BlogPostForm()

    return render(request, 'blog/add_post.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BlogPostForm

def eadd_blog(request):
    """Allow the logged-in expert to add a new blog post and update their blog count."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.is_public = True
            blog_post.author_id = request.session['user_id']
            blog_post.save()

            # Update the expert's blog count
            try:
                # Get the expert using the login relationship
                login = Login.objects.get(login_id=request.session['user_id'])
                expert = Expert.objects.get(login=login)
                expert.blog_count += 1
                expert.save()
            except (Expert.DoesNotExist, Login.DoesNotExist):
                messages.error(request, 'Expert profile not found.')
                return redirect('blog:blog_dashboard')

            messages.success(request, 'Blog post added successfully!')
            return redirect('blog:blog_dashboard')
    else:
        form = BlogPostForm()

    return render(request, 'blog/eadd_blog.html', {'form': form})






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
            return redirect('blog:admin_blog_dashboard')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form})




def eedit_blog_post(request, post_id):
    """Allow the logged-in user to edit their own blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog:blog_dashboard')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/eedit_post.html', {'form': form, 'post': post})



def delete_blog_post(request, post_id):
    """Allow the logged-in user to soft delete their own blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    try:
        post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
        post.is_deleted = True  # Set the is_deleted flag instead of deleting
        post.save()
        messages.success(request, 'Blog post moved to trash successfully!')
        return redirect('blog:dashboard')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found.')
        return redirect('blog:dashboard')

def restore_blog_post(request, post_id):
    """Allow the logged-in user to restore their soft-deleted blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    try:
        post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
        post.is_deleted = False  # Reset the is_deleted flag
        post.save()
        messages.success(request, 'Blog post restored successfully!')
        return redirect('blog:dashboard')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found.')
        return redirect('blog:dashboard')




def adelete_blog_post(request, post_id):
    """Allow the logged-in user to soft delete their own blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    try:
        post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
        post.is_deleted = True  # Set the is_deleted flag instead of deleting
        post.save()
        messages.success(request, 'Blog post moved to trash successfully!')
        return redirect('blog:admin_blog_dashboard')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found.')
        return redirect('blog:admin_blog_dashboard')

def arestore_blog_post(request, post_id):
    """Allow the logged-in user to restore their soft-deleted blog post."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')

    try:
        post = get_object_or_404(BlogPost, id=post_id, author_id=request.session['user_id'])
        post.is_deleted = False  # Reset the is_deleted flag
        post.save()
        messages.success(request, 'Blog post restored successfully!')
        return redirect('blog:admin_blog_dashboard')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found.')
        return redirect('blog:admin_blog_dashboard')

from django.shortcuts import render, redirect
from django.utils.timezone import now
from .models import BlogPost, BlogComment, BlogBookmark
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BlogPost, BlogComment
from django.http import HttpResponse

from django.db.models import Q

def blog_home(request):
    """Render the blog homepage with published and non-deleted blog posts, comments, and allow users to comment after login."""
    user_logged_in = ensure_user_logged_in(request)  # Check if the user is logged in
    user_id = request.session.get('user_id') if user_logged_in else None  # Get user ID from session if logged in

    # Get the search query from the request
    query = request.GET.get('q', '')  # Default to empty string if no query is provided

    # Filter posts based on the search query, published status, and not deleted
    posts = BlogPost.objects.filter(
        Q(title__icontains=query) |  # Search by title (case-insensitive)
        Q(content__icontains=query)   # Search by content (case-insensitive)
    ).filter(
        status='published',           # Only published posts
        is_deleted=False             # Only non-deleted posts
    ).order_by('-created_at')

    # Handle new comment submission
    if request.method == 'POST' and user_logged_in:  # Only process comment if the user is logged in
        comment_text = request.POST.get('comment')
        post_id = request.POST.get('post_id')
        parent_comment_id = request.POST.get('parent_comment_id', None)

        if comment_text:
            try:
                # Ensure commenting only on published and non-deleted posts
                post = BlogPost.objects.get(
                    id=post_id, 
                    status='published',
                    is_deleted=False
                )
                user = User_Reg.objects.get(uid=user_id)

                if parent_comment_id:
                    parent_comment = BlogComment.objects.get(id=parent_comment_id)
                    new_comment = BlogComment(post=post, user=user, comment=comment_text, parent_comment=parent_comment)
                else:
                    new_comment = BlogComment(post=post, user=user, comment=comment_text)

                new_comment.save()
                messages.success(request, 'Your comment has been posted!')
            except BlogPost.DoesNotExist:
                messages.error(request, 'This post is no longer available.')
            except Exception as e:
                messages.error(request, 'An error occurred while posting your comment.')

        return redirect('blog:home')  # After submitting the comment, redirect to the homepage

    context = {
        'posts': posts,
        'user_logged_in': user_logged_in,
        'query': query
    }

    return render(request, 'blog/home.html', context)

from django.shortcuts import redirect
from django.contrib import messages

def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=post_id)
        user = User_Reg.objects.get(uid=request.session['user_id'])
        comment_text = request.POST.get('comment')
        BlogComment.objects.create(post=post, user=user, comment=comment_text)
        messages.success(request, 'Comment added successfully!')
    return redirect('blog:home')

def add_reply(request, comment_id):
    if request.method == 'POST':
        parent_comment = get_object_or_404(BlogComment, id=comment_id)
        user = User_Reg.objects.get(uid=request.session['user_id'])
        reply_text = request.POST.get('reply')
        BlogComment.objects.create(post=parent_comment.post, user=user, comment=reply_text, parent_comment=parent_comment)
        messages.success(request, 'Reply added successfully!')
    return redirect('blog:home')

from userauths.models import Login, User_Reg

def blog_detail(request, post_id):
    """Render the detailed view of a single blog post with comments."""
    post = get_object_or_404(BlogPost, id=post_id, is_public=True)
    comments = post.comments.all()

    if request.method == 'POST':
        if not ensure_user_logged_in(request):
            return redirect('userauths:login')

        comment_text = request.POST.get('comment')
        try:
            # Fetch the logged-in user using the correct primary key field `uid`
            user = User_Reg.objects.get(uid=request.session['user_id'])
            BlogComment.objects.create(post=post, user=user, comment=comment_text)
            messages.success(request, 'Comment added successfully!')
        except User_Reg.DoesNotExist:
            messages.error(request, 'An error occurred while adding your comment. Please try again.')
            return redirect('userauths:login')

        return redirect('blog:detail', post_id=post_id)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BlogPost, BlogPostLike
import json
@csrf_exempt
def like_blog_post(request):
    """Handle liking/unliking a blog post."""
    if request.method == 'POST':
        # Ensure the user is logged in
        if not ensure_user_logged_in(request):
            return JsonResponse({'error': 'User not logged in'}, status=403)
        
        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            post = get_object_or_404(BlogPost, id=post_id)
            user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))

            # Check if the user has already liked the post
            existing_like = BlogPostLike.objects.filter(post=post, user=user).first()

            if existing_like:
                # Unlike the post
                existing_like.delete()
                post.like_count -= 1
                like_added = False
            else:
                # Like the post
                BlogPostLike.objects.create(post=post, user=user)
                post.like_count += 1
                like_added = True

            post.save()
            # Return the like count and if the post was liked
            return JsonResponse({'like_count': post.like_count, 'like_added': like_added}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def admin_blog_dashboard(request):
    """Render the admin dashboard for blog post management."""
    if not ensure_user_logged_in(request):
        return redirect('userauths:login')
        
    # Get the user's login record
    try:
        user_login = Login.objects.get(login_id=request.session['user_id'])
        user = user_login.uid  # Get the User_Reg instance
        

        # Get all posts with related data
        posts = BlogPost.objects.select_related('author').prefetch_related(
            'comments'
        ).order_by('-created_at')

        # Get statistics
        stats = {
            'total_posts': posts.count(),
            'published_posts': posts.filter(is_public=True).count(),
            'draft_posts': posts.filter(is_public=False).count(),
            'total_comments': sum(post.comments.count() for post in posts),
            'total_likes': sum(post.like_count for post in posts)
        }

        context = {
            'posts': posts,
            'stats': stats,
            'is_admin': True,
            'user': user
        }
        
        return render(request, 'blog/admin_blog_dashboard.html', context)
        
    except Login.DoesNotExist:
        messages.error(request, 'User session is invalid.')
        return redirect('userauths:login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('blog:dashboard')