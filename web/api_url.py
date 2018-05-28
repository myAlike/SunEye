from django.conf.urls import url

from web import views

urlpatterns = [
    url(r'multitask/cmd/$', views.multitask_cmd, name='multitask_cmd'),
    url(r'multitask/res/$', views.multitask_res),
    url(r'multitask/file_download/(\d+)/$', views.file_download, name='file_download_url'),
    url(r'multitask/file_upload/(\w+)/$', views.multitask_file_upload, name='file_upload'),
    url(r'multitask/file_upload/(\w+)/delete/$', views.delete_file, name='delete_file'),
    url(r'multitask/file/$', views.multitask_file, name='multitask_file'),
    url(r'multitask/action/$', views.multitask_task_action, name='multitask_action'),
    url(r'token/gen/$', views.token_gen, name='token_gen'),
    url(r'dashboard_summary/$', views.dashboard_summary, name='dashboard_summary'),
    url(r'dashboard_detail/$', views.dashboard_detail, name='dashboard_detail'),
    url(r'audit/user_counts/$', views.user_login_counts, name='user_login_counts'),
    url(r'audit/cmd_logs/$', views.audit_cmd_logs)
]
