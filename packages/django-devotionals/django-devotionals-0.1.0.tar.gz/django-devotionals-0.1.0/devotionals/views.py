import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.conf.urls.defaults import *
from django.template import loader, RequestContext
from django.views.generic import DetailView, ListView 
from django.views.generic.dates import YearMixin, MonthMixin

from devotionals.models import Devotional

class DevotionalDetailView(DetailView):
    model=Devotional


class PostDetailView(DetailView):
    model=Post
    template_name_field = 'blog__template_name'

    def get_queryset(self):
        if not WITHOUT_SETS:
            queryset=Post.published_objects.all().filter(blog__blog_set__slug=self.kwargs['blog_set_slug'], blog__slug=self.kwargs['blog_slug'], publish_date__year=self.kwargs['year'])
        else:
            queryset=Post.published_objects.all().filter(
                blog__slug=self.kwargs['blog_slug'],
                publish_date__year=self.kwargs['year'],
                slug=self.kwargs['slug'])
        return queryset

class PostCreateView(CreateView):
    form_class=PostForm
    template_name='devotionals/post_create.html'

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        context['blog'] = Blog.published_objects.get(slug=self.kwargs['slug'])
        return context

class PostUpdateView(UpdateView):
    form_class=PostForm
    template_name='devotionals/post_update.html'
    queryset=Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)
        context['blog'] = Blog.published_objects.get(slug=self.kwargs['blog_slug'])
        return context

class PostDeleteView(DeleteView):
    model=Post
    template_name='devotionals/post_delete.html'
    success_url='/blogs/' 

