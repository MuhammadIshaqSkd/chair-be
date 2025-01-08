def mark_messages_as_read(messages_queryset):
    messages_queryset.filter(is_read=False).update(is_read=True)