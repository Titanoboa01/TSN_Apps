from prometheus_client import start_http_server, Gauge
import subprocess
import re
import time
from datetime import datetime

sequence_id_metric = Gauge('send_sequence_id', 'Sequence ID metric', ['src_ip', 'dst_ip', 'run_id'])
send_interval_metric = Gauge('send_interval', 'Send interval metric', ['src_ip', 'dst_ip', 'run_id'])
send_offset_metric = Gauge('send_offset', 'Send offset metric', ['src_ip', 'dst_ip', 'run_id'])
graficon_metric = Gauge('graficon', 'grafikon adatok', ['src_ip', 'dst_ip', 'run_id'])

def parse_and_collect_send_output():
    process = subprocess.Popen(['./send', '--dst-ip=10.1.1.75'], stdout=subprocess.PIPE, text=True)
    src_ip = None
    dst_ip = None
    send_interval = None
    start_offset = None
    run_id = None
    for line in iter(process.stdout.readline, ''):
        if 'preferred src' in line:
            match = re.search(r'preferred src ([\d\.]+)', line)
            if match:
                src_ip = match.group(1)
        if 'dst' in line:
            match = re.search(r'dst ([\d\.]+)', line)
            if match:
                dst_ip = match.group(1)
        if 'Send interval' in line:
            match = re.search(r'Send interval ([\d]+) us', line)
            if match:
                send_interval = int(match.group(1))
        if 'start offset' in line:
            match = re.search(r'start offset ([\d]+) us', line)
            if match:
                start_offset = int(match.group(1))
        if 'sending' in line:
            match = re.search(r'sending (\d+) at (\d+\.\d+)', line)
            if match:
                sequence_id = int(match.group(1))
                send_time = float(match.group(2))
                if run_id is None and send_interval is not None:
                    run_id = str(int(time.time()))
                sequence_id_metric.labels(src_ip, dst_ip, run_id).set(sequence_id)
                send_interval_metric.labels(src_ip, dst_ip, run_id).set(send_interval)
                send_offset_metric.labels(src_ip, dst_ip, run_id).set(start_offset)
                if run_id is not None and send_interval is not None:
                    theoretical_send_time = float(run_id) + (sequence_id-1) * (send_interval / 1_000_000)
                    diff = send_time - theoretical_send_time
                    graficon_metric.labels(src_ip, dst_ip, run_id).set(diff)

if __name__ == '__main__':
    start_http_server(6000)

    parse_and_collect_send_output()
