import subprocess


def ermittle_ip_adresse() -> str:
    konsole_out = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
    return [zeile
            for zeile
            in konsole_out.stdout.split("\n") if "inet 192.168.2" in zeile][0].split('/')[0].strip().split(" ")[1]
