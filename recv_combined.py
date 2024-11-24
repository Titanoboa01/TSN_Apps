import requests
import subprocess
import re
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

def parse_and_send_recv_output():
    process = subprocess.Popen(['./recv', '--iface', 'eno1d1'], stdout=subprocess.PIPE, text=True)
    src_ip, dst_ip, run_id = None, None, None
    try:
        for line in iter(process.stdout.readline, ''):
            if 'ETH IPv4' in line:
                match = re.search(r'IPv4 ([\d\.]+) -> ([\d\.]+)', line)
                if match:
                    src_ip = match.group(1)
                    dst_ip = match.group(2)
                match = re.search(r'sequenceId (\d+) time (\d+\.\d+) RX SW (\d+\.\d+) HW (\d+\.\d+)', line)
                if match:
                    sequence_id = int(match.group(1))
                    recv_send_time = Decimal(match.group(2))
                    recv_rx_sw = Decimal(match.group(3))
                    recv_rx_hw = Decimal(match.group(4))
                    if run_id is None:
                        run_id = match.group(2).split('.')[0]

                    tags = f"src_ip={src_ip},dst_ip={dst_ip},run_id={run_id}"
                    fields = (f"recv_sequence_id={Decimal(sequence_id)},recv_send_time={Decimal(recv_send_time):.9f},recv_rx_sw={Decimal(recv_rx_sw):.9f},recv_rx_hw={Decimal(recv_rx_hw):.9f}")
                    send_to_influxdb("recv_metrics", tags, fields)
    except KeyboardInterrupt:
        print("\nExit")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    parse_and_send_recv_output()
