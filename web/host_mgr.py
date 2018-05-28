import json
import os
import signal
import subprocess

from django.db import transaction

from SunEye import settings
from backstage.utils import json_date_handler
from web import models


class MultiTask(object):
    def __init__(self, task_type, request_ins):
        self.request = request_ins
        self.task_type = task_type

    def run(self):
        return self.parse_args()

    def parse_args(self):
        task_func = getattr(self, self.task_type)
        return task_func()

    def terminate_task(self):
        task_id = self.request.POST.get('task_id')
        assert task_id.isdigit()
        task_obj = models.TaskLog.objects.get(id=int(task_id))
        res_msg = ''
        try:
            os.killpg(task_obj.task_pid, signal.SIGTERM)
            res_msg = 'Task %s has terminated!' % task_id
        except OSError as e:
            res_msg = "Error happened when tries to terminate task %s , err_msg[%s]" % (task_id, str(e))
        return res_msg

    def run_cmd(self):
        cmd = self.request.POST.get('cmd')
        host_ids = [int(i.split('host_')[-1]) for i in json.loads(self.request.POST.get("selected_hosts"))]
        task_expire_time = self.request.POST.get("expire_time")
        exec_hosts = models.BindHosts.objects.filter(id__in=host_ids)
        random_str = self.request.POST.get('local_file_path')
        task_obj = self.create_task_log('cmd', exec_hosts, task_expire_time, cmd, random_str)
        p = subprocess.Popen(['python3',
                              settings.MultiTaskScript,
                              '-task_type', 'cmd',
                              '-expire', task_expire_time,
                              '-uid', str(self.request.user.id),
                              '-task', cmd,
                              '-task_id', str(task_obj.id)
                              ],
                             preexec_fn=os.setsid)
        task_obj.task_pid = p.pid
        task_obj.save()
        return task_obj.id

    def get_task_result(self, detail=True):
        """get multi run task result"""
        task_id = self.request.GET.get('task_id')
        log_dic = {
            # 'summary':{},
            'detail': {}
        }
        task_obj = models.TaskLog.objects.get(id=int(task_id))
        task_detail_obj_list = models.TaskLogDetail.objects.filter(child_of_task_id=task_obj.id)
        log_dic['summary'] = {
            'id': task_obj.id,
            'start_time': task_obj.start_time,
            'end_time': task_obj.end_time,
            'task_type': task_obj.task_type,
            'host_num': task_obj.hosts.select_related().count(),
            'finished_num': task_detail_obj_list.filter(result='success').count(),
            'failed_num': task_detail_obj_list.filter(result='failed').count(),
            'unknown_num': task_detail_obj_list.filter(result='unknown').count(),
            'content': task_obj.cmd,
            'expire_time': task_obj.expire_time
        }

        if detail:
            for log in task_detail_obj_list:
                log_dic['detail'][log.id] = {
                    'date': log.date,
                    'bind_host_id': log.bind_host_id,
                    'host_id': log.bind_host.host.id,
                    'hostname': log.bind_host.host.hostname,
                    'ip_addr': log.bind_host.host.ip_addr,
                    'username': log.bind_host.host_user.username,
                    'system': log.bind_host.host.system_type,
                    'event_log': log.event_log,
                    'result': log.result,
                    'note': log.note
                }

        return json.dumps(log_dic, default=json_date_handler)

    @transaction.atomic
    def create_task_log(self, task_type, hosts, expire_time, content, random_str=None, note=None):
        task_log_obj = models.TaskLog(
            task_type=task_type,
            user=self.request.user,
            cmd=content,
            files_dir=random_str,
            expire_time=int(expire_time),
            note=note
        )
        task_log_obj.save()
        task_log_obj.hosts.add(*hosts)

        for h in hosts:
            task_log_detail_obj = models.TaskLogDetail(
                child_of_task_id=task_log_obj.id,
                bind_host_id=h.id,
                event_log='',
                result='unknown'
            )
            task_log_detail_obj.save()

        return task_log_obj

    def file_send(self):
        params = json.loads(self.request.POST.get('params'))
        print("params:", params)
        host_ids = [int(i.split('host_')[-1]) for i in params.get("selected_hosts")]
        task_expire_time = params.get("expire_time")
        random_str = params.get('local_file_path')
        exec_hosts = models.BindHosts.objects.filter(id__in=host_ids)
        task_type = self.request.POST.get('task_type')
        # local_file_list = params.get('local_file_list')
        if task_type == 'file_send':
            local_file_list = os.listdir("%s/task_data/tmp/%s" % (settings.FileUploadDir, random_str))

            content = "send local files %s to remote path [%s]" % (local_file_list, params.get('remote_file_path'))

        else:
            local_file_list = 'not_required'  # set this var just for passing verification
            content = "download remote file [%s]" % params.get('remote_file_path')

        task_obj = self.create_task_log(task_type, exec_hosts, task_expire_time, content, random_str)
        if task_type == 'file_get':
            local_path = "%s/task_data/%s" % (settings.FileUploadDir, task_obj.id)
            try:
                os.makedirs(local_path, exist_ok=True)
            except OSError as e:
                print("err:", e)

        p = subprocess.Popen(['python3',
                              settings.MultiTaskScript,
                              '-task_type', task_type,
                              '-expire', task_expire_time,
                              '-uid', str(self.request.user.id),
                              # '-local',' '.join(local_file_list) ,
                              '-remote', params.get('remote_file_path'),
                              '-task_id', str(task_obj.id)
                              ], preexec_fn=os.setsid)

        task_obj.task_pid = p.pid
        task_obj.save()
        return task_obj.id
