from django import forms
from django.utils.safestring import mark_safe

from web import models

from kingadmin.admin_base import site, BaseKingAdmin

from django.shortcuts import render, HttpResponse


class IDCAdmin(BaseKingAdmin):
    list_display = ('id', 'name','log_details')
    list_per_page = 2

    # readonly_table = True

    def default_form_validation(self):
        print("-----customer validation ", self)
        print("----instance:", self.instance)

        consult_content = self.cleaned_data.get("name", '')
        if len(consult_content) < 4:
            return forms.ValidationError(
                ('Field %(field)s 不能少于4个字符'),
                code='invalid',
                params={'field': "name", },
            )

    def log_details(self):
        '''日志详情'''
        ele = '''<a href="/kingadmin/web/" >详情</a> '''
        return ele

    log_details.display_name = '日志详情'


class HostAdmin(BaseKingAdmin):
    search_fields = ('hostname', 'ip_addr')
    list_display = ('hostname', 'idc', 'system_type', 'create_at',)
    list_filter = ('idc', 'system_type', 'create_at')
    readonly_fields = ['ip_addr', ]
    actions = ["test", "delete_selected_objs"]

    def test(self, request, querysets):
        print("in test", )
        return HttpResponse('dfdfd')

    test.short_description = "测试动作"

    def clean_memo(self):
        print("name clean validation:", self.cleaned_data["memo"])
        if not self.cleaned_data["memo"]:
            self.add_error('memo', "cannot be null")


class HostUserAdmin(BaseKingAdmin):
    # list_display = ('auth_method', 'username', 'password')
    list_filter = ('auth_method', 'username')
    colored_fields = {
        'username': '#83e277',
    }


class BindHostAdmin(BaseKingAdmin):
    list_display = ('host', 'host_user')
    list_filter = ('host', 'host_user')



class HostGroupAdmin(BaseKingAdmin):
    list_display = ('name', 'bind_hosts')
    list_filter = ('name', 'bind_hosts')
    filter_horizontal = ('bind_hosts',)
    readonly_fields = ['bind_hosts', ]


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        if len(password1) < 6:
            raise forms.ValidationError("Passwords takes at least 6 letters")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(BaseKingAdmin):
    add_form = UserCreationForm

    list_display = ('id', 'name', 'email','groups', 'host_groups', 'bind_hosts')
    filter_horizontal = ('groups', 'host_groups', 'bind_hosts')
    readonly_fields = ['password','host_groups', 'name']

    search_fields = ['email', 'name']
    list_filter = ['name']
    change_page_onclick_fields = {
        'password': ['password_change_form', '重置密码']
    }


site.register(models.UserProfile, UserAdmin)
site.register(models.IDC, IDCAdmin)
site.register(models.Hosts, HostAdmin)
site.register(models.HostUsers, HostUserAdmin)
site.register(models.HostUsers, HostUserAdmin)
site.register(models.HostGroups, HostGroupAdmin)
site.register(models.BindHosts, BindHostAdmin)
site.register(models.BindHosts, BindHostAdmin)
