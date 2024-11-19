from prometheus_client import start_http_server, Gauge
import subprocess
import re
import time
from datetime import datetime

sequence_id_metric = Gauge('recv_sequence_id', 'Sequence ID metric', ['src_ip', 'dst_ip', 'run_id'])
recv_rx_hw_metric = Gauge('recv_rx_hw', 'Receive RX HW metric', ['src_ip', 'dst_ip', 'run_id'])
recv_rx_sw_metric = Gauge('recv_rx_sw', 'Receive RX SW metric', ['src_ip', 'dst_ip', 'run_id'])
run_id_metric = Gauge('recv_run_id', 'Run ID metric', ['src_ip', 'dst_ip', 'run_id'])
recv_send_time_metric = Gauge('recv_send_time', 'Recv send time metric', ['src_ip', 'dst_ip', 'run_id'])

def parse_and_collect_recv_output():
    process = subprocess.Popen(['./recv', '--iface', 'eno1d1'], stdout=subprocess.PIPE, text=True)
    run_id = None
    src_ip = None
    dst_ip = None
    for line in iter(process.stdout.readline, ''):
        if 'ETH IPv4' in line:
            match = re.search(r'IPv4 ([\d\.]+) -> ([\d\.]+)', line)
            if match:
                src_ip = match.group(1)
                dst_ip = match.group(2)
        if 'sequenceId' in line:
            match = re.search(r'sequenceId (\d+) time (\d+\.\d+) RX SW (\d+\.\d+) HW (\d+\.\d+)', line)
            if match:
                sequence_id = int(match.group(1))
                if run_id is None:
                    run_id = match.group(2).split('.')[0]
                send_time = float(match.group(2))
                recv_rx_sw = float(match.group(3))
                recv_rx_hw = float(match.group(4))

                if src_ip is not None and dst_ip is not None:
                    sequence_id_metric.labels(src_ip, dst_ip, run_id).set(sequence_id)
                    recv_send_time_metric.labels(src_ip, dst_ip, run_id).set(send_time)
                    recv_rx_hw_metric.labels(src_ip, dst_ip, run_id).set(recv_rx_hw)
                    recv_rx_sw_metric.labels(src_ip, dst_ip, run_id).set(recv_rx_sw)

if __name__ == '__main__':
    start_http_server(6011)

    parse_and_collect_recv_output()
