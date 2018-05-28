"""SunEye URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from web import views
from web import api_url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^kingadmin/', include('kingadmin.urls')),
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^hosts/$', views.hosts, name='host_list'),
    url(r'^hosts/multi/$', views.hosts_multi, name="batch_cmd_exec"),
    url(r'^multi_task/log/deatail/(\d+)/$', views.multi_task_log_detail, name='multi_task_log_detail'),
    url(r'^hosts/multi/filetrans$', views.hosts_multi_filetrans, name="batch_file_transfer"),
    url(r'^host/detail/', views.host_detail),
    url(r'^api/', include(api_url)),
    url(r'^personal/', views.personal, name='personal'),
    url(r'^user_audit/(\d+)/$', views.user_audit, name='user_audit'),
    url(r'^logout/', views.logout, name='logout'),

    url(r'^login/$', views.login, name='login'),
    url(r'^accounts/profile/$', views.personal),

]
