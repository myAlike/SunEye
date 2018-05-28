from django import forms
from django.forms.models import ModelForm


def __new__(cls, *args, **kwargs):
    # self.fields['customer_note'].widget.attrs['class'] = 'form-control'
    # disabled_fields = ['qq', 'consultant']
    for field_name in cls.base_fields:
        field = cls.base_fields[field_name]
        # print("field repr",field_name,field.__repr__())
        attr_dic = {'placeholder': field.help_text}
        if 'BooleanField' not in field.__repr__():
            attr_dic.update({'class': 'form-control'})
            # print("-->field",field)
            if 'ModelChoiceField' in field.__repr__():  # fk field
                attr_dic.update({'data-tag': field_name})
                # if 'DateTimeField' in field.__repr__():
                #     attr_dic.update({'placeholder': field_name})
        if cls.Meta.form_create is False:
            if field_name in cls.Meta.admin.readonly_fields:
                attr_dic['disabled'] = True
                # print('----read only:',field_name)
        field.widget.attrs.update(attr_dic)

        if hasattr(cls.Meta.admin, "clean_%s" % field_name):
            clean_field_func = getattr(cls.Meta.admin, "clean_%s" % field_name)
            setattr(cls, "clean_%s" % field_name, clean_field_func)
    else:
        if hasattr(cls.Meta.model, "clean2"):  # clean2 is kingadmin's own clean method
            clean_func = getattr(cls.Meta.model, "clean")
            setattr(cls, "clean", clean_func)
        else:  # use default clean method
            setattr(cls, "clean", default_clean)

    return ModelForm.__new__(cls)


def default_clean(self):
    '''form defautl clean method'''
    if self.Meta.admin.readonly_table is True:
        raise forms.ValidationError(("This is a readonly table!"))

    if self.errors:
        raise forms.ValidationError(("Please fix errors before re-submit."))
    if self.instance.id is not None:
        for field in self.Meta.admin.readonly_fields:
            old_field_val = getattr(self.instance, field)
            if hasattr(old_field_val, "select_related"):  # m2m
                print('select_related-----',getattr(old_field_val, "select_related")())
                m2m_objs = getattr(old_field_val, "select_related")()
                m2m_vals = [i[0] for i in m2m_objs.values_list('id')]
                set_m2m_vals = set(m2m_vals)
                set_m2m_vals_from_frontend = set([i.id for i in self.cleaned_data.get(field)])
                print("m2m", m2m_vals, set_m2m_vals_from_frontend)
                if set_m2m_vals != set_m2m_vals_from_frontend:
                    raise forms.ValidationError(("readonly field"))
                continue
            form_val = self.cleaned_data[field]
            print("filed differ compare:", old_field_val,'=======', form_val)
            if old_field_val != form_val:
                self.add_error(field, "Readonly Field: field should be '{value}' ,not '{new_value}' ".format(
                    **{'value': old_field_val, 'new_value': form_val}))

    response = self.Meta.admin.default_form_validation(self)
    if response:
        raise forms.ValidationError(response)


def create_form(fields, admin_class, form_create=False, **kwargs):
    class Meta:
        pass

    setattr(Meta, 'model', admin_class.model)
    setattr(Meta, 'fields', fields)
    setattr(Meta, 'admin', admin_class)
    setattr(Meta, 'form_create', form_create)

    name = 'DynamicModelForm'
    attrs = {'Meta': Meta}

    model_form = type(name, (ModelForm,), attrs)
    setattr(model_form, '__new__', __new__)
    setattr(model_form, 'clean', default_clean)
    if kwargs.get("request"):  # for form validator
        setattr(model_form, '_request', kwargs.get("request"))

    return model_form
