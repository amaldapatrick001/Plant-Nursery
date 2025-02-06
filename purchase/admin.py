from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'view_comment', 'view_reply', 'review_date', 'delete_review')
    search_fields = ('user__fname', 'product__name', 'comment')
    list_filter = ('rating', 'review_date')
    readonly_fields = ('review_date',)
    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'rating', 'comment', 'review_date', 'reply'),
        }),
    )

    def view_comment(self, obj):
        """ Show a preview of the comment """
        return obj.comment[:50]  # Display only the first 50 characters of the comment
    view_comment.short_description = 'Comment'

    def view_reply(self, obj):
        """ Show a preview of the reply """
        return obj.reply[:50]  # Display only the first 50 characters of the reply
    view_reply.short_description = 'Reply'

    def delete_review(self, obj):
        """ Provide a button to delete the review if necessary """
        # Display a button or link to delete the review (this will use Django's delete functionality)
        return f'<a href="/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.id}/delete/" class="button">Delete</a>'
    delete_review.short_description = 'Delete Review'
    delete_review.allow_tags = True  # Allow HTML rendering for the delete button/link

    def save_model(self, request, obj, form, change):
        """ Custom save method to handle replies and updates """
        # You can add custom logic here if needed (e.g., automatic reply, validation)
        super().save_model(request, obj, form, change)

admin.site.register(Review, ReviewAdmin)
