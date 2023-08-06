from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^form/$', 'invitable.views.form', name="invitable_form"),
)
