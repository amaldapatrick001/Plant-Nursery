from django import forms
from .models import BlogPost
import re

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'images', 'videos', 'status']

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if title and not title[0].isupper():
            raise forms.ValidationError("The first letter of the title must be uppercase.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if content:
            # Ensure sentences start with uppercase letters and space after a period.
            sentences = re.split(r'(?<=[.?!])\s+', content)
            for sentence in sentences:
                if sentence and not sentence[0].isupper():
                    raise forms.ValidationError(
                        "Each sentence should start with an uppercase letter."
                    )
        return content

    from django.core.exceptions import ValidationError
import mimetypes

def clean_images(self):
    images = self.cleaned_data.get('images')

    if images:
        # Check if the file has a valid mime type (image type)
        mime_type, _ = mimetypes.guess_type(images.name)
        
        # You can use the mime_type to check the file type
        if mime_type not in ['image/jpeg', 'image/png', 'image/gif']:
            raise forms.ValidationError("Invalid image format. Only JPEG, PNG, or GIF images are allowed.")
    
    return images


    def clean_videos(self):
        videos = self.cleaned_data.get('videos', None)
        valid_video_formats = ['video/mp4', 'video/mov', 'video/avi', 'video/wmv', 'video/x-msvideo', 'video/webm', 'video/x-flv']
        if videos and videos.content_type not in valid_video_formats:
            raise forms.ValidationError("Only MP4, MOV, AVI, WMV, AVCHD, WebM, and FLV formats are supported.")
        return videos

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        images = cleaned_data.get("images")
        videos = cleaned_data.get("videos")
        
        # At least one of content, images, or videos must be provided.
        if not any([content, images, videos]):
            raise forms.ValidationError("At least one of 'Content', 'Images', or 'Videos' must be filled.")
