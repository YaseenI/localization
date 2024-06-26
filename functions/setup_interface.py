import subprocess

def setup_interface(interface, mon_interface):
    global monitor_interface
    # Commands to set up the interface for monitoring
    subprocess.call(["sudo", "ifconfig", interface, "down"])
    subprocess.call(["sudo", "airmon-ng", "start", interface])
    # Adjust for your environment - some systems rename the interface to wlan0mon
    monitor_interface = mon_interface
    subprocess.call(["sudo", "ifconfig", monitor_interface, "up"])
    print(f"{monitor_interface} set to monitor mode and brought up.")
    return monitor_interface