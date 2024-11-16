from prometheus_client import start_http_server, Gauge
import subprocess
import re
import time
from datetime import datetime

sequence_id_metric = Gauge('recv_sequence_id', 'Sequence ID metric', ['src_ip', 'dst_ip', 'run_id'])
recv_rx_hw_metric = Gauge('recv_rx_hw', 'Receive RX HW metric', ['src_ip', 'dst_ip', 'run_id'])
recv_rx_sw_metric = Gauge('recv_rx_sw', 'Receive RX SW metric', ['src_ip', 'dst_ip', 'run_id'])
send_time_metric = Gauge('send_time', 'Send time metric', ['src_ip', 'dst_ip', 'run_id'])

def parse_and_collect_recv_output():
    process = subprocess.Popen(['./recv', '--iface', 'ens3'], stdout=subprocess.PIPE, text=True)
    run_id = None
    for line in iter(process.stdout.readline, ''):
        if 'sequenceId' in line:
            match = re.search(r'sequenceId (\d+) time (\d+\.\d+) RX SW (\d+\.\d+) HW (\d+\.\d+)', line)
            if match:
                sequence_id = int(match.group(1))
                if run_id is None:
                    run_id = match.group(2).split('.')[0]
                send_time = float(match.group(2))
                recv_rx_sw = match.group(3)
                recv_rx_hw = match.group(4)
                sequence_id_metric.labels('10.1.1.75', '10.1.1.193', run_id).set(sequence_id)
                send_time_metric.labels('10.1.1.75', '10.1.1.193', run_id).set(send_time)
                recv_rx_hw_metric.labels('10.1.1.75', '10.1.1.193', run_id).set(float(recv_rx_hw))
                recv_rx_sw_metric.labels('10.1.1.75', '10.1.1.193', run_id).set(float(recv_rx_sw))

if __name__ == '__main__':
    start_http_server(6001)
    
    parse_and_collect_recv_output()
