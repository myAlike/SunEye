from django.http import HttpResponse
from django.shortcuts import render, redirect


class BaseKingAdmin(object):
    add_form = None
    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 1
    readonly_fields = []
    ordering = None
    filter_horizontal = []
    actions = ["delete_selected_objs", ]
    readonly_table = False
    change_page_onclick_fields = {}

    def default_form_validation(self):
        """用户可以在此进行自定义的表单验证，相当于django form的clean方法"""
        pass

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        if self.readonly_table:
            errors = {"readonly_table": "This table is readonly_table , cannot be deleted or modified! "}
        else:
            errors = {}
        if request.POST.get("_delete_confirm") == "yes":
            if not self.readonly_table:
                querysets.delete()
                return redirect("/kingadmin/%s/%s/" % (app_name, model_name))
        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request, "kingadmin/table_objs_delete.html", {"objs": querysets,
                                                                    "admin_class": self,
                                                                    "app_name": app_name,
                                                                    "model_name": model_name,
                                                                    "model_verbose_name": self.model._meta.verbose_name,
                                                                    "admin_action": request._admin_action,
                                                                    "errors": errors,
                                                                    "selected_ids": selected_ids
                                                                    })


class AdminSite(object):
    def __init__(self, name="admin"):
        self.enabled_admins = {}
        self.name = name

    def register(self, model_class, admin_class):
        if model_class._meta.app_label not in self.enabled_admins:
            self.enabled_admins[model_class._meta.app_label] = {}
        admin_class.model = model_class
        self.enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class


site = AdminSite()
