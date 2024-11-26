import requests
import subprocess
import re
import time
from decimal import Decimal

INFLUXDB_URL = "http://193.224.20.121:5050/api/v2/write"
INFLUXDB_BUCKET = "tsn_data"
INFLUXDB_ORG = "tsn_org"
INFLUXDB_TOKEN = "cVk0-k1WE_TxDC4LXRjKRTaitiSoYamrZdL_fjKaAsRUBw8sP2F3FBYIerLBcSypf3nZg723MNIM-zqBK03egQ=="

def send_to_influxdb(measurement, tags, fields):
    line_protocol = f"{measurement},{tags} {fields}"
    print(f"DEBUG: {line_protocol}")
    headers = {"Authorization": f"Token {INFLUXDB_TOKEN}"}
    response = requests.post(
        f"{INFLUXDB_URL}?bucket={INFLUXDB_BUCKET}&org={INFLUXDB_ORG}&precision=ns",
        headers=headers,
        data=line_protocol
    )
    if response.status_code != 204:
        print(f"Failed to write to InfluxDB: {response.text}")
def parse_and_send_send_output():
    process = subprocess.Popen(['./send', '--sockprio=1', '--offset', '400', '--interval', '1000', '--iface', 'eno1d1', '--dst-ip=10.10.1.2'], stdout=subprocess.PIPE, text=True)
    src_ip, dst_ip, send_interval, start_offset, run_id = None, None, None, None, None
    try:
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
                    send_time = Decimal(match.group(2))
                    if run_id is None and send_interval is not None:
                        run_id = match.group(2).split('.')[0]
                    tags = f"src_ip={src_ip},dst_ip={dst_ip},run_id={run_id}"
                    fields = f"send_sequence_id={Decimal(sequence_id)},send_time={Decimal(send_time):.9f},run_id_metric={Decimal(run_id)},send_interval={Decimal(send_interval)},start_offset={Decimal(start_offset)}"
                    send_to_influxdb("send_metrics", tags, fields)
    except KeyboardInterrupt:
        print("\nExit")
        process.terminate()
        process.wait()
if __name__ == "__main__":
    parse_and_send_send_output()

