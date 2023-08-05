from django.views.generic import DateDetailView, ArchiveIndexView

class BlogPostMixin(object):
    def get_paginate_by(self, queryset):
        return settings.BLOG_PAGINATE_BY

    def get_queryset(self, *args, **kwargs):
        lookup = {}

        if not self.request.user.has_perm('blog.can_read_private'):
            lookup['is_public'] = True

        if 'author' in self.kwargs:
            lookup['author__username'] = self.kwargs['author']

        if 'tag' in self.kwargs:
            lookup['category__slug'] = self.kwargs['tag']

        return Post.on_site.all().filter(**lookup)

    def get_allow_future(self):
        return self.request.user.has_perm('blog.can_read_private')

    def get_date_field(self):
        return 'pub_date'

class BlogPostDetailView(DateDetailView, BlogPostMixin):
    pass

class BlogPostListView(ArchiveIndexView, BlogPostMixin):
    pass

