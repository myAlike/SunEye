from django.db.models import Q

from web import models

models.BindHosts.objects.filter()


def table_filter(request, admin_class):
    filter_conditions = {}
    if hasattr(admin_class, 'list_display'):
        for condition in admin_class.list_display:
            if request.GET.get(condition):
                filed_type = admin_class.model._meta.get_field(condition).__repr__()
                # print('filed_type', filed_type)
                if 'ForeignKey' in filed_type:
                    filter_conditions['%s_id' % condition] = request.GET.get(condition)
                elif 'DateTimeField' in filed_type:
                    filter_conditions['%s__gt' % condition] = request.GET.get(condition)
                else:
                    filter_conditions[condition] = request.GET.get(condition)


    return admin_class.model.objects.filter(**filter_conditions), filter_conditions


def table_search(request, admin_class, querysets):
    search_key = request.GET.get('_q', "")
    q_obj = Q()
    q_obj.connector = "OR"
    for column in admin_class.search_fields:
        q_obj.children.append(("%s__contains" % column, search_key))
    return querysets.filter(q_obj)


def table_order(request, search_querysets, admin_class):
    orderby_field = request.GET.get('orderby')
    if orderby_field:
        order_field = orderby_field.strip()
        orderby_column_index = admin_class.list_display.index(orderby_field.strip('-'))
        objs = search_querysets.order_by(order_field)

        if order_field.startswith('-'):
            order_field = order_field.strip('-')
        else:
            order_field = '-%s' % order_field

        return [objs, order_field, orderby_column_index]
    return [search_querysets, orderby_field, None]
