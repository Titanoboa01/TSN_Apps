import requests
import subprocess
import re
import time

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

def parse_and_collect_taprio():
    process = subprocess.Popen(['tc', 'qdisc', 'show', 'dev', 'eno1d1'], stdout=subprocess.PIPE, text=True)
    output = process.communicate()[0]

    for line in output.splitlines():
        if 'index' in line and 'gatemask' in line:
            match = re.search(r'index (\d+) cmd S gatemask 0x(\w+) interval (\d+)', line)
            if match:
                gate_index = int(match.group(1))
                gatemask_hex = match.group(2)
                interval = int(match.group(3))

                gate_id = int(gatemask_hex, 16).bit_length() - 1

                tags = f"device=eno1d1,gate_id={gate_id},gate_index={gate_index}"
                fields = f"interval={interval}"
                send_to_influxdb("taprio_metrics", tags, fields)

if __name__ == "__main__":
    try:
        while True:
            parse_and_collect_taprio()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exit")

