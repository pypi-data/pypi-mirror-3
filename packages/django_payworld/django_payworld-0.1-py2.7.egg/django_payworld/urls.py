from django.conf.urls.defaults import patterns, include, url

from django_payworld import views

urlpatterns = patterns('',
    url(r'^success/$', views.success, name='payworld-success'),
    url(r'^failure/$', views.failure, name='payworld-failure'),
    url(r'^result/$', views.result, name='payworld-result'),
)

