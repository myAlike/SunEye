import subprocess
import time

from backstage import audit
from backstage import utils


def get_session_id(instance, bind_host_obj, tag):
    '''apply  session id'''
    session_obj = instance.models.Session(user_id=instance.login_user.id, bind_host=bind_host_obj, tag=tag)

    session_obj.save()
    # print('session id:', session_obj)
    return session_obj


def login_raw(instance, h):
    ip, port, username, password = h.host.ip_addr, h.host.port, h.host_user.username, h.host_user.password
    ssh_path = instance.django_settings.SSH_CLIENT_PATH
    rand_tag_id = utils.random_str(16)
    session_obj = get_session_id(instance, h, rand_tag_id)
    session_track_process = subprocess.Popen(
        "/bin/sh %s/backend/session_tracker.sh %s  %s" % (
        instance.django_settings.BASE_DIR, session_obj.id, rand_tag_id),
        shell=True,
        cwd=instance.django_settings.BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    cmd_str = "sshpass -p %s %s %s@%s -p%s -Z %s -o StrictHostKeyChecking=no" % (
    password, ssh_path, username, ip, port, rand_tag_id)

    subprocess.run(cmd_str, shell=True)

    session_obj.stay_time = time.time() - session_obj.date.timestamp()
    session_log_file = "%s/%s/session_%s.log" % (instance.django_settings.SESSION_AUDIT_LOG_DIR,
                                                 session_obj.date.strftime("%Y_%m_%d"),
                                                 session_obj.id
                                                 )
    log_parser = audit.AuditLogHandler(session_log_file)
    log_data = log_parser.parse()
    session_obj.cmd_count = len(log_data)
    session_obj.save()
