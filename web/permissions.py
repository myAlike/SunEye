from django.shortcuts import render, redirect
from django.urls import resolve

from SunEye import settings
from kingadmin.permission_list import perm_dict


def perm_check(*args, **kwargs):
    request = args[0]
    resolve_url_obj = resolve(request.path)
    current_url_name = resolve_url_obj.url_name  # 当前url的url_name
    print(request.user.is_authenticated, '=====', dir(request.user.is_authenticated))
    if request.user.is_authenticated is False:
        return redirect(settings.LOGIN_URL)

    match_flag = False
    match_key = None
    for per_key, per_val in perm_dict.items():
        per_url_name, per_method, per_args = per_val
        if per_url_name == current_url_name:
            if per_method == request.method:
                if not per_args:
                    match_flag = True
                    match_key = per_key
                else:
                    for item in per_args:
                        request_method_fun = getattr(request, per_method)
                        if request_method_fun.get(item, None):
                            match_flag = True
                        else:
                            match_flag = False
                            break
                    if match_flag == True:
                        match_key = per_key
                        break

    if match_flag:
        app_name, *per_name = match_key.split('_')
        perm_obj = '%s.%s' % (app_name, match_key)

        if request.user.has_perm(perm_obj):
            print('当前用户有此权限')
            return True
        else:
            print('当前用户没有该权限')
            return False

    else:
        print("未匹配到权限项，当前用户无权限")


def check_permission(func):
    def inner(*args, **kwargs):
        if not perm_check(*args, **kwargs):
            request = args[0]
            return render(request, 'page_403.html')
        return func(*args, **kwargs)

    return inner
