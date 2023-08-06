from django.conf.urls import patterns, include, url


urlpatterns = patterns('luxuryadmin.views',
    url(r'^collection/$', 'collection', name="collection"),
    url(r'^xhr/upload/photo/$', 'xhr_upload_photo', name="xhr_upload_photo"),
    url(r'^xhr/login/$', 'xhr_log_in', name="xhr_log_in"),

    url(r'^xhr/product/(?P<pk>[0-9]*)/save/$', 'xhr_save_product',
        name="xhr_save_product"),
    url(r'^xhr/product/(?P<pk>[0-9]*)/save/(?P<type>[a-z]+)/$', 'xhr_save_product',
        name="xhr_save_product"),
    url(r'^xhr/product/create/$', 'xhr_save_product', name="xhr_save_product"),
    url(r'^xhr/update_photos/$', 'xhr_update_photos',
        name="xhr_update_photos"),
    url(r'^log_out/$', 'log_out', name="log_out"),
)
