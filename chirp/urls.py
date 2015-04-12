from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'chirp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'chirp_app.views.index'),
    url(r'^login$', 'chirp_app.views.login_view'),
    url(r'^logout$', 'chirp_app.views.logout_view'),
    url(r'^signup$', 'chirp_app.views.signup'),
    url(r'^chirps$', 'chirp_app.views.public'),
    url(r'^submit$', 'chirp_app.views.submit'),
)
