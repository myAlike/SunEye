from django.conf.urls import url

from kingadmin import views

urlpatterns = [
    url(r'^login/$', views.acc_login, name="acc_login"),
    url(r'^logout/$', views.acc_logout, name="acc_logout"),
    url(r'^(\w+)/(\w+)/change/(\d+)/password/$', views.password_reset_form, name='password_reset'),

    url(r'^$', views.app_idex, name='table_index'),
    url(r'^(\w+)/$', views.app_tables, name='app_tables'),
    url(r'^(\w+)/(\w+)/$', views.display_table_list, name='table_list'),
    url(r'^(\w+)/(\w+)/add/$', views.table_add, name="table_add"),
    url(r'^(\w+)/(\w+)/change/(\d+)/$', views.table_change, name="table_change"),
    url(r'^(\w+)/(\w+)/delete/(\d+)$', views.table_del, name='table_del'),
]
