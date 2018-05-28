import re
from datetime import datetime, timedelta

from django import template
from django.core.exceptions import FieldDoesNotExist
from django.urls import reverse as url_reverse
from django.utils.safestring import mark_safe

register = template.Library()

from web import models

models.BindHosts.objects.filter()


@register.simple_tag
def get_table_name(adim_class):
    return adim_class.model._meta.verbose_name


@register.simple_tag
def load_search_element(adim_class, search_text):
    if adim_class.search_fields:
        placeholder = "search by %s" % ",".join(adim_class.search_fields)
        ele = '''
                    <div class="searchbox">
                       <form method="get">
                            <div class="input-group custom-search-form">
                                <input type="text" name="_q" value='%s' class="form-control" placeholder="%s">
                                <span class="input-group-btn">
                                    <button class="text-muted" type="SUBMIT"><i class="fa fa-search"></i></button>
                                </span>
                            </div>
                       </form>
                   </div>

                ''' % (search_text, placeholder)
        return mark_safe(ele)
    return ''


@register.simple_tag
def get_table_column(admin_class, display_data):
    if hasattr(admin_class.model, display_data):
        return admin_class.model._meta.get_field(display_data).verbose_name
    else:
        if hasattr(admin_class, display_data):
            field_func = getattr(admin_class, display_data)
            if hasattr(field_func, 'display_name'):
                return field_func.display_name
            return field_func.__name__


@register.simple_tag
def verbose_name(filter_column, admin_class):
    col_obj = admin_class.model._meta.get_field(filter_column)
    return col_obj.verbose_name


@register.simple_tag
def filter_column_choice(filter_field, admin_class, filter_condtions):
    select_ele = '''<select class="form-control" name='{filter_field}' ><option value=''>----</option>'''
    field_obj = admin_class.model._meta.get_field(filter_field)
    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            # print("choice", choice_item, filter_condtions.get(filter_field), type(filter_condtions.get(filter_field)))
            if filter_condtions.get(filter_field) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ == "ForeignKey":

        selected = ''
        for choice_item in field_obj.get_choices()[1:]:
            filter_field_id = '%s_id' % filter_field
            if filter_condtions.get(filter_field_id) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value='%s' %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''
    if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
        date_els = []

        today_ele = datetime.now().date()
        date_els.append([datetime.now().date(), '今天'])
        date_els.append([today_ele - timedelta(days=1), "昨天"])
        date_els.append([today_ele - timedelta(days=7), "近7天"])
        date_els.append([today_ele.replace(day=1), "本月"])
        date_els.append([today_ele - timedelta(days=30), "近30天"])
        date_els.append([today_ele - timedelta(days=90), "近90天", ])
        date_els.append([today_ele - timedelta(days=180), "近180天"])
        date_els.append([today_ele.replace(month=1, day=1), "本年"])
        date_els.append([today_ele - timedelta(days=365), "近一年"])

        selected = ''
        for item in date_els:
            select_ele += '''<option value='%s' %s>%s</option>''' % (item[0], selected, item[1])

        filter_field_name = filter_field

    else:
        filter_field_name = filter_field
    select_ele += "</select>"
    select_ele = select_ele.format(filter_field=filter_field_name)

    return mark_safe(select_ele)


@register.simple_tag
def build_table_header_column(column, orderby_key, filter_condtions, admin_class):
    filters = ''
    for k, v in filter_condtions.items():
        filters += "&%s=%s" % (k, v)

    ele = '''<th><a href="?{filters}&orderby={orderby_key}">{column}</a>
    {sort_icon}
    </th>'''
    if orderby_key:
        if orderby_key.startswith("-"):
            sort_icon = '''<span class="glyphicon glyphicon-chevron-up"></span>'''
        else:
            sort_icon = '''<span class="glyphicon glyphicon-chevron-down"></span>'''

        if orderby_key.strip("-") == column:  # 排序的就是这个字段
            orderby_key = orderby_key
        else:
            orderby_key = column
            sort_icon = ''

    else:  # 没有排序
        orderby_key = column
        sort_icon = ''
    try:
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name.upper()
    except FieldDoesNotExist as e:
        column_verbose_name = getattr(admin_class, column).display_name.upper()
        ele = '''<th><a href="javascript:void(0);">{column}</a></th>'''.format(column=column_verbose_name)
        return mark_safe(ele)
    ele = ele.format(orderby_key=orderby_key, column=column_verbose_name, sort_icon=sort_icon, filters=filters)
    return mark_safe(ele)


@register.simple_tag
def build_table_row(request, row_obj, admin_class, onclick_column=None, target_link=None):
    row_ele = '<tr>'
    row_ele += "<td><input type='checkbox' tag='row-check' value='%s' > </td>" % row_obj.id
    if admin_class.list_display:
        for index, column_name in enumerate(admin_class.list_display):
            if hasattr(row_obj, column_name):
                field_obj = row_obj._meta.get_field(column_name)
                if field_obj.choices:  # choices type  外键
                    column_data = getattr(row_obj, "get_%s_display" % column_name)()
                else:
                    column_data = getattr(row_obj, column_name)

                if 'DateTimeField' in field_obj.__repr__():
                    column_data = getattr(row_obj, column_name).strftime("%Y-%m-%d %H:%M:%S")
                if 'ManyToManyField' in field_obj.__repr__():
                    column_data = getattr(row_obj, column_name).select_related().count()

                column = "<td>%s</td>" % column_data
                if column_name in getattr(admin_class, 'colored_fields') if \
                        hasattr(admin_class, 'colored_fields') else {}:  # 特定字段需要显示color
                    color_dic = getattr(admin_class, 'colored_fields')
                    if column_name in color_dic:
                        column = "<td style='background-color:%s'>%s</td>" % (color_dic[column_name],
                                                                              column_data)
                    else:
                        column = "<td>%s</td>" % column_data

                if index == 0:  # 首列可点击进入更改页
                    column = '''<td><a class='btn-link'  href='%schange/%s/' >%s</a> </td> ''' % (request.path,
                                                                                                  row_obj.id,
                                                                                                  column_data)



            elif hasattr(admin_class, column_name):
                field_func = getattr(admin_class, column_name)
                admin_class.instance = row_obj
                admin_class.request = request
                column = "<td>%s</td>" % (field_func())

            row_ele += column
        row_ele += "</tr>"
        return mark_safe(row_ele)
    else:
        row_ele += "<td><a class='btn-link'  href='{request_path}change/{obj_id}/' >{column}</a></td>". \
            format(request_path=request.path, column=row_obj, obj_id=row_obj.id)
    row_ele += "</tr>"
    return mark_safe(row_ele)


@register.simple_tag
def render_page_num(request, paginator_obj, loop_counter):
    abs_full_url = request.get_full_path()

    if "?page=" in abs_full_url:
        url = re.sub("page=\d+", "page=%s" % loop_counter, request.get_full_path())
    elif "?" in abs_full_url:
        url = "%s&page=%s" % (request.get_full_path(), loop_counter)
    else:
        url = "%s?page=%s" % (request.get_full_path(), loop_counter)

    if loop_counter == paginator_obj.number:
        return mark_safe('''<li class='active'><a href="{abs_url}">{page_num}</a></li>''' \
                         .format(abs_url=url, page_num=loop_counter))
    if abs(loop_counter - paginator_obj.number) < 2 or \
                    loop_counter == 1 or loop_counter == paginator_obj.paginator.num_pages:  # the first page or last

        return mark_safe('''<li><a href="{abs_url}">{page_num}</a></li>''' \
                         .format(abs_url=url, page_num=loop_counter))
    elif abs(loop_counter - paginator_obj.number) < 3:
        return mark_safe('''<li><a href="{abs_url}">...</a></li>''' \
                         .format(abs_url=url, page_num=loop_counter))
    else:
        return ''


@register.simple_tag
def render_page_previous(request, paginator_obj):
    url = re.sub("page=\d+", "page=%s" % (paginator_obj.number - 1), request.get_full_path())
    return mark_safe(
        '''<li><a href = "{abs_url}" aria-label = "Previous" > <span aria-hidden = "true" >«</span></a></li>'''.format(
            abs_url=url))


@register.simple_tag
def render_page_next(request, paginator_obj):
    url = re.sub("page=\d+", "page=%s" % (paginator_obj.number + 1), request.get_full_path())
    return mark_safe(
        '''<li><a href = "{abs_url}" aria-label = "Next" > <span aria-hidden = "true" >»</span></a></li>'''.format(
            abs_url=url))


@register.simple_tag
def load_admin_actions(admin_class):
    select_ele = '<select id="admin_action" name="admin_action" class="form-control"><option value="">----</option>'
    for option in admin_class.actions:
        action_display_name = option
        if hasattr(admin_class, option):
            action_func = getattr(admin_class, option)
            if hasattr(action_func, 'short_description'):
                action_display_name = action_func.short_description
        select_ele += ("<option value='%s'>" % option) + action_display_name + "</options>"
    select_ele += "</select>"

    return mark_safe(select_ele)


def recursive_related_objs_lookup(objs):
    # model_name = objs[0]._meta.model_name
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = '''<li><span class='btn-link'> %s:</span> %s </li>''' % (
            obj._meta.verbose_name, obj.__str__().strip("<>"))
        ul_ele += li_ele

        # for local many to many
        ##print("------- obj._meta.local_many_to_many", obj._meta.local_many_to_many)
        for m2m_field in obj._meta.local_many_to_many:  # 把所有跟这个对象直接关联的m2m字段取出来了
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj, m2m_field.name)  # getattr(customer, 'tags')
            for o in m2m_field_obj.select_related():  # customer.tags.select_related()
                li_ele = '''<li> %s: %s </li>''' % (m2m_field.verbose_name, o.__str__().strip("<>"))
                sub_ul_ele += li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele  # 最终跟最外层的ul相拼接

        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():

                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    # print("-------ManyToManyRel",accessor_obj,related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                        target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele = "<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li> <span class='btn-link'>%s</span>: %s </li>''' % (
                                o._meta.verbose_name, o.__str__().strip("<>"))
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj, related_obj.get_accessor_name())
                # 上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                    target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    # print("one to one i guess:",accessor_obj)
                    target_objs = [accessor_obj]
                # print("target_objs",target_objs)
                if len(target_objs) > 0:
                    ##print("\033[31;1mdeeper layer lookup -------\033[0m")
                    # nodes = recursive_related_objs_lookup(target_objs,model_name)
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele += "</ul>"
    return ul_ele


@register.simple_tag
def display_obj_related(objs):
    return mark_safe(recursive_related_objs_lookup(objs))


@register.simple_tag
def add_fk_search_btn(form_obj, field):
    ##print("add_fk_search_btn",field)
    ##print("add_fk_search_btn",dir(field))
    ##print("form",form_obj.__dict__)
    ##print("---fields",form_obj.instance._meta.get_fields())
    for field_obj in form_obj.instance._meta.get_fields():
        # print("=--",repr(field_obj))
        if field.name == field_obj.name:
            if 'ForeignKey' in repr(field_obj):
                if field.name not in form_obj.Meta.admin.readonly_fields:
                    ele = '''
                        <i style="cursor: pointer" data-target="#modal-dialog" data-toggle="modal"
                        class="fa fa-search" aria-hidden="true"
                        onclick="PrepareFilterSearch('%s')"></i>''' % field.name
                    return mark_safe(ele)
    return ''


@register.simple_tag
def add_onclick_link(form_obj, field_obj):
    '''
    在表的修改页面给配置好的change_page_onclick_field加link
    :param form_obj:
    :param field_obj:
    :return:
    '''
    if field_obj.name in form_obj.Meta.admin.change_page_onclick_fields:
        # link_url = url_reverse(form_obj.Meta.admin.change_page_onclick_fields[field_obj.name][0],
        #                        args=(form_obj.instance.id,))
        link_ele = '''<a class="btn-link" href="%s/" >%s</a>''' % \
                   (form_obj.Meta.admin.change_page_onclick_fields[field_obj.name][0],
                    form_obj.Meta.admin.change_page_onclick_fields[field_obj.name][1],
                    )
        return mark_safe(link_ele)
    return ''


@register.simple_tag
def decorate_date_field(form_obj, field_obj):
    # print("repr...",field_obj)
    # print("repr.field..",dir(field_obj.field))
    field_type = repr(form_obj.Meta.model._meta.get_field(field_obj.name))
    filed_val = getattr(form_obj.instance, field_obj.name)
    if 'DateTimeField' in field_type:
        field_ele = '''

        <div style="margin-left:-10px" class="col-md-7 dp-component">
            <div class="input-group date">
                <input id="id_%s" name="%s" type="text"  value="%s" class="form-control">
                <span class="input-group-addon"><i class="fa fa-calendar fa-lg"></i></span>

            </div>
        </div>
        <div class="col-md-5 input-group date">
            <input class="tp-textinput form-control" type="text" >
            <span class="input-group-addon"><i class="fa fa-clock-o fa-lg"></i></span>
        </div>
        ''' % (field_obj.name, field_obj.name, filed_val)
        return mark_safe(field_ele)
    return ''


@register.simple_tag
def get_m2m_objs(field_name, model_obj):
    try:
        m2m_objs = getattr(model_obj, field_name)
        return m2m_objs.model.objects.all()
    except ValueError as e:
        # print(e)
        return model_obj._meta.model.bind_hosts.through.bindhosts.get_queryset()


@register.simple_tag
def get_chosen_m2m_objs(form_field_obj, model_obj):
    selected_pks = form_field_obj.value()
    try:
        m2m_objs = getattr(model_obj, form_field_obj.name)
        selected_objs = m2m_objs.select_related().filter(id__in=selected_pks)
        return selected_objs
    except ValueError as e:
        return []


@register.simple_tag
def check_disabled_attr(field_name, form_obj):
    if form_obj.Meta.form_create is True:
        return ''
    if field_name in form_obj.Meta.admin.readonly_fields:
        return 'disabled'
