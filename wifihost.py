import subprocess

def run(cmd):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"[ERROR] {cmd}\n{result.stderr}")
    else:
        print(f"[OK] {cmd}")
    return result.stdout.strip()

def connect_to_wifi(ssid, password):
    run(f"nmcli device wifi connect '{ssid}' password '{password}'") #need to input our wifi buddy's friend ssid and password 

def create_hotspot(ap_ssid, ap_password):
    run("nmcli connection delete my-hotspot")  # Remove old hotspot if exists
    run(f"nmcli connection add type wifi ifname wlan0 con-name my-hotspot autoconnect yes ssid '{ap_ssid}'")
    run("nmcli connection modify my-hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared")
    run("nmcli connection modify my-hotspot wifi-sec.key-mgmt wpa-psk")
    run(f"nmcli connection modify my-hotspot wifi-sec.psk '{ap_password}'")
    run("nmcli connection up my-hotspot")

# Example usage
connect_to_wifi("SSID", "yourpassword123")
create_hotspot("Pi_AP", "raspberry123")
