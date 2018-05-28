from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, Http404, redirect, HttpResponse, HttpResponseRedirect

from kingadmin import tables, forms
from kingadmin.king_admin import site
from kingadmin.permissions import check_permission


# Create your views here.
@login_required(login_url="/kingadmin/login")
def app_idex(request):
    return render(request, 'kingadmin/app_index.html', {'enabled_admins': site.enabled_admins
                                                        })

# @check_permission
@login_required(login_url="/kingadmin/login/")
def app_tables(request, app_name):
    enabled_admins = {app_name: site.enabled_admins[app_name]}
    return render(request, 'kingadmin/app_index.html', {'enabled_admins': enabled_admins,
                                                        'current_app': app_name
                                                        })


@login_required(login_url="/kingadmin/login/")
def display_table_list(request, app_name, table_name):
    if app_name in site.enabled_admins:
        if table_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][table_name]
            if request.method == "POST":
                selected_ids = request.POST.get("selected_ids")
                action = request.POST.get("admin_action")
                # print('action', action, "delete_selected_objs")
                action = str(action)

                if selected_ids:
                    selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
                else:
                    raise KeyError("No object selected.")
                if hasattr(admin_class, action):
                    action_func = getattr(admin_class, action)
                    request._admin_action = action
                    # print('_admin_action', request._admin_action)
                    return action_func(admin_class, request, selected_objs)

            querysets, filter_conditions = tables.table_filter(request, admin_class)
            search_querysets = tables.table_search(request, admin_class, querysets)
            order_querysets = tables.table_order(request, search_querysets, admin_class)

            paginator = Paginator(order_querysets[0], admin_class.list_per_page)

            page = request.GET.get('page')
            try:
                table_obj_list = paginator.page(page)
            except PageNotAnInteger:
                table_obj_list = paginator.page(1)
            except EmptyPage:
                table_obj_list = paginator.page(paginator.num_pages)

            return render(request, 'kingadmin/model_obj_list.html', {'app_name': app_name,
                                                                     'table_name': table_name,
                                                                     'admin_class': admin_class,
                                                                     'table_obj_list': table_obj_list,
                                                                     'paginator': paginator,
                                                                     'filter_conditions': filter_conditions,
                                                                     'search_text': request.GET.get('_q', ''),
                                                                     "orderby_key": order_querysets[1],
                                                                     })
    else:
        raise Http404()


@login_required(login_url="/kingadmin/login/")
def table_del(request, app_name, table_name, obj_id):
    if app_name in site.enabled_admins:
        if table_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][table_name]
            objs = admin_class.model.objects.filter(id=obj_id)
            if request.method == "POST":
                delete_tag = request.POST.get("_delete_confirm")
                if delete_tag == "yes":
                    objs.delete()
                    return redirect("/kingadmin/%s/%s/" % (app_name, table_name))
            if admin_class.readonly_table is True:
                return render(request, 'kingadmin/table_objs_delete.html')
            return render(request, 'kingadmin/table_objs_delete.html',
                          {'model_verbose_name': admin_class.model._meta.verbose_name,
                           'model_name': admin_class.model._meta.model_name,
                           'model_db_table': admin_class.model._meta.db_table,
                           'objs': objs,
                           'app_name': app_name,
                           'obj_id': obj_id
                           })


@login_required(login_url="/kingadmin/login/")
def table_add(request, app_name, model_name):
    if app_name in site.enabled_admins:
        if model_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][model_name]
            fields = []
            for field_obj in admin_class.model._meta.fields:
                if field_obj.editable:
                    fields.append(field_obj.name)
            for field_obj in admin_class.model._meta.many_to_many:
                fields.append(field_obj.name)
            if admin_class.add_form == None:
                model_form = forms.create_form(fields,
                                               admin_class,
                                               form_create=True,
                                               request=request)
            else:  # this admin has customized  creation form defined
                model_form = admin_class.add_form
            if request.method == 'GET':
                form_obj = model_form()
            elif request.method == "POST":
                form_obj = model_form(request.POST)
                if form_obj.is_valid():
                    form_obj.validate_unique()
                    if form_obj.is_valid():
                        form_obj.save()

            return render(request, 'kingadmin/table_add.html',
                          {'form_obj': form_obj,
                           'model_name': admin_class.model._meta.model_name,
                           'model_verbose_name': admin_class.model._meta.verbose_name,
                           'model_db_table': admin_class.model._meta.db_table,
                           'admin_class': admin_class,
                           'app_name': app_name,
                           'active_url': '/kingadmin/',
                           })
    else:
        return Http404('url %s/%s not found' % (app_name, model_name))


@login_required(login_url="/kingadmin/login/")
def table_change(request, app_name, model_name, obj_id):
    if app_name in site.enabled_admins:
        if model_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][model_name]
            obj = admin_class.model.objects.get(id=obj_id)
            fields = []
            for field_obj in admin_class.model._meta.fields:
                if field_obj.editable:
                    fields.append(field_obj.name)

            for field_obj in admin_class.model._meta.many_to_many:
                fields.append(field_obj.name)
            model_form = forms.create_form(fields, admin_class, request=request)

            if request.method == "GET":
                form_obj = model_form(instance=obj)
            elif request.method == "POST":
                # print("post:",request.POST)
                form_obj = model_form(request.POST, instance=obj)
                if form_obj.is_valid():
                    form_obj.validate_unique()
                    if form_obj.is_valid():
                        form_obj.save()
            return render(request, 'kingadmin/table_change.html',
                          {'form_obj': form_obj,
                           'active_url': '/kingadmin/',
                           'model_verbose_name': admin_class.model._meta.verbose_name,
                           'model_name': admin_class.model._meta.model_name,
                           'app_name': app_name,
                           'admin_class': admin_class

                           })



def acc_login(request):
    err_msg = {}
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            request.session.set_expiry(60 * 60)
            return HttpResponseRedirect(request.GET.get("next") if request.GET.get("next") else "/kingadmin/")

        else:
            err_msg["error"] = 'Wrong username or password!'

    return render(request, 'kingadmin/login.html',{'err_msg':err_msg})


def acc_logout(request):
    logout(request)
    return HttpResponseRedirect("/kingadmin/login/")


def password_reset_form(request, app_name, table_db_name, user_id):
    user_obj = request.user._meta.model.objects.get(id=user_id)
    can_change_user_password = False
    if request.user.is_superuser or request.user.id == user_id:
        can_change_user_password = True

    if can_change_user_password:
        if request.method == "GET":
            change_form = site.enabled_admins[app_name][table_db_name].add_form(instance=user_obj)
        else:
            change_form = site.enabled_admins[app_name][table_db_name].add_form(request.POST, instance=user_obj)
            if change_form.is_valid():
                change_form.save()
                url = "/%s/" % request.path.strip("/password/")
                return redirect(url)
        return render(request, 'kingadmin/password_change.html', {'user_obj': user_obj,
                                                                  'form': change_form})
    else:
        return HttpResponse("Only admin user has permission to change password")
