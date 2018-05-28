import django
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


# Create your models here.

class IDC(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'idc'
        verbose_name_plural = 'idc'


class Department(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'


class Hosts(models.Model):
    hostname = models.CharField(max_length=64, unique=True)
    ip_addr = models.GenericIPAddressField(unique=True)
    system_type_choices = (
        ('windows', 'Windows'),
        ('linux', 'Linux/Unix'),
    )
    system_type = models.CharField(choices=system_type_choices, max_length=32, default='linux')
    port = models.IntegerField(default=22)
    idc = models.ForeignKey('IDC', on_delete=models.DO_NOTHING)
    enabled = models.BooleanField(default=True, help_text='主机若不想被用户访问可以去掉此选项')
    memo = models.CharField(max_length=64, blank=True, null=True)
    create_at = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return '%s(%s)' % (self.hostname, self.ip_addr)

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = '主机'


class HostUsers(models.Model):
    auth_method_choices = (
        ('ssh-password', 'SSH/ Password'),
        ('ssh-key', 'SSH/KEY'),
    )
    auth_method = models.CharField(choices=auth_method_choices, max_length=32)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64, blank=True, null=True)
    memo = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '%s(%s)' % (self.username, self.password)

    class Meta:
        verbose_name = '远程用户'
        verbose_name_plural = '远程用户'


class BindHosts(models.Model):
    host = models.ForeignKey('Hosts', on_delete=models.DO_NOTHING)
    host_user = models.ForeignKey('HostUsers', on_delete=models.DO_NOTHING)

    def __str__(self):
        return '%s(%s)' % (self.host, self.host_user)

    class Meta:
        unique_together = ("host", "host_user")
        verbose_name = '主机与远程用户绑定'
        verbose_name_plural = '主机与远程用户绑定'


class HostGroups(models.Model):
    name = models.CharField(max_length=64, unique=True)
    memo = models.CharField(max_length=128, blank=True, null=True)
    bind_hosts = models.ManyToManyField("BindHosts")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '主机组'
        verbose_name_plural = '主机组'


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        # self.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_active = True
        user.is_superuser = True
        # user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """账号"""
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True
    )
    password = models.CharField(_('password'), max_length=128,
                                help_text=mark_safe('''<a href='password/'>修改密码</a>'''))
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    department = models.ForeignKey('Department', verbose_name="部门", blank=True, on_delete=models.DO_NOTHING)
    host_groups = models.ManyToManyField('HostGroups', verbose_name="主机组", blank=True)
    bind_hosts = models.ManyToManyField('BindHosts', verbose_name="授权主机", blank=True, null=True)

    memo = models.TextField('备注', blank=True, null=True, default=None)
    date_join = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    valid_begin_time = models.DateTimeField(default=django.utils.timezone.now, help_text="yyyy-mm-dd HH:MM:SS")
    valid_end_time = models.DateTimeField(blank=True, null=True, help_text="yyyy-mm-dd HH:MM:SS")

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_active

class SessionTrack(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    def __str__(self):
        return '%s' %self.id


class Session(models.Model):
    '''生成用户操作session id '''
    user = models.ForeignKey('UserProfile', on_delete=models.DO_NOTHING)
    bind_host = models.ForeignKey('BindHosts', on_delete=models.DO_NOTHING)
    tag = models.CharField(max_length=128,default='n/a')
    closed = models.BooleanField(default=False)
    cmd_count = models.IntegerField(default=0) #命令执行数量
    stay_time = models.IntegerField(default=0, help_text="每次刷新自动计算停留时间",verbose_name="停留时长(seconds)")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '<id:%s user:%s bind_host:%s>' % (self.id,self.user.email,self.bind_host.host)
    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'


#Deprecated
class AuditLog(models.Model):
    session = models.ForeignKey(SessionTrack, on_delete=models.DO_NOTHING)
    user = models.ForeignKey('UserProfile', on_delete=models.DO_NOTHING)
    host = models.ForeignKey('BindHosts', on_delete=models.DO_NOTHING)
    action_choices = (
        (0,'CMD'),
        (1,'Login'),
        (2,'Logout'),
        (3,'GetFile'),
        (4,'SendFile'),
        (5,'exception'),
    )
    action_type = models.IntegerField(choices=action_choices,default=0)
    cmd = models.TextField(blank=True,null=True)
    memo = models.CharField(max_length=128,blank=True,null=True)
    date = models.DateTimeField()


    def __str__(self):
        return '%s-->%s@%s:%s' %(self.user.email,self.host.host_user.username,self.host.host.ip_addr,self.cmd)
    class Meta:
        verbose_name = '审计日志old'
        verbose_name_plural = '审计日志old'


class TaskLog(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    task_type_choices = (
        ('cmd', 'CMD'),
        ('file_send', "批量发送文件"),
        ('file_get', "批量下载文件")
    )
    task_type = models.CharField(choices=task_type_choices, max_length=64)
    file_dir = models.CharField('文件上传', max_length=64, blank=True, null=True)
    user = models.ForeignKey('UserProfile', on_delete=models.DO_NOTHING)
    hosts = models.ManyToManyField('BindHosts')
    cmd = models.TextField()
    expire_time = models.IntegerField(default=30)
    task_pid = models.IntegerField(default=0)
    note = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "taskid:%s cmd:%s" % (self.id, self.cmd)

    class Meta:
        verbose_name = '批量任务'
        verbose_name_plural = '批量任务'


class TaskLogDetail(models.Model):
    child_of_task = models.ForeignKey('TaskLog', on_delete=models.DO_NOTHING)
    bind_host = models.ForeignKey('BindHosts', on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)  # finished date
    event_log = models.TextField()
    result_choices = (('success', 'Success'), ('failed', 'Failed'), ('unknown', 'Unknown'))
    result = models.CharField(choices=result_choices, max_length=30, default='unknown')
    note = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "child of:%s result:%s" % (self.child_of_task.id, self.result)

    class Meta:
        verbose_name = '批量任务日志'
        verbose_name_plural = '批量任务日志'


class Token(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    host = models.ForeignKey(BindHosts, on_delete=models.DO_NOTHING)
    token = models.CharField(max_length=64)
    date = models.DateTimeField(default=django.utils.timezone.now)
    expire = models.IntegerField(default=300)

    def __str__(self):
        return '%s : %s' % (self.host.host.ip_addr, self.token)

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
