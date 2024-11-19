from prometheus_client import start_http_server, Gauge
import subprocess
import re
import time

gate_interval_metric = Gauge('taprio_gate_interval', 'Interval time for each gate', ['gate_id'])

def parse_tc_output():
    """
    Futtatja a `tc qdisc show dev eno1d1` parancsot, és kinyeri a `gatemask`-hoz és `interval`-hoz tartozó adatokat.
    """
    try:
        result = subprocess.check_output(['tc', 'qdisc', 'show', 'dev', 'eno1d1'], text=True)
        
        for match in re.finditer(r'gatemask (0x[0-9a-fA-F]+) interval (\d+)', result):
            gatemask = match.group(1)
            interval = int(match.group(2))

            gate_id = int(gatemask, 16).bit_length() - 1

            gate_interval_metric.labels(gate_id=gate_id).set(interval)
            print(f"Frissített metrika: gate_id={gate_id}, interval={interval}")

    except subprocess.CalledProcessError as e:
        print(f"Hiba a tc parancs futtatása közben: {e}")
    except Exception as e:
        print(f"Általános hiba: {e}")

if __name__ == '__main__':
    start_http_server(6012)

    print("Taprio exporter fut...")
    while True:
        parse_tc_output()
        time.sleep(1)

