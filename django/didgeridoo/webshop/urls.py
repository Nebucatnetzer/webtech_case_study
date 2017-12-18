from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^details/(?P<article_id>[0-9]+)/$',
        views.article_details,
        name='details'),
    url(r'^category/(?P<category_id>[0-9]+)/$',
        views.articles_in_category,
        name='category'),
]
