from django.test import TestCase

# Create your tests here.
from django.utils.safestring import mark_safe


def log_details():
    '''日志详情'''
    ele = '''<a class='btn-link' href='/kingadmin/web/>详情</a> '''
    return mark_safe(ele)
