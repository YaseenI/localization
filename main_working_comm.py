import threading
import queue
import time
import random
import subprocess
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Elt
from functions.threads.receive_data import receive_data, send_data
from functions.threads import radar
from functions.threads.packet_sniffer import packet_sniffer
from functions.threads.sync_probes import sync_probes
from functions.threads.update import update
from objects.proberequest import ProbeRequest
from objects.device import Device
from functions import extract_vendor_specific, setup_interface
from functions.threads import radar



def run():
    while True:
        try:
            to_run = int(input("How many threads to run (1-5): "))
            if 1 <= to_run <= 5:
                break  # Exit the loop if the number is valid
            else:
                print("Number must be between 1 and 5.")
        except ValueError:
            print("Please enter a valid integer.")

    while True:
        run_radar = input("Do you want to run the radar? (y/n): ").lower()
        if run_radar == 'y':
            break
        elif run_radar == 'n':
            while True:
                coordinates = input("Please enter sniffer coordinates (in the format: a b): ")
                # Split the input string into two numbers
                nums = coordinates.split()
                if len(nums) != 2:
                    print("Invalid input. Please enter two numbers separated by a space.")
                    continue
                try:
                    x, y = map(int, nums)
                    print("Coordinates entered:", (x, y))
                    break
                except ValueError:
                    print("Invalid input. Please enter valid integers for coordinates.")
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    
    while True:
        try:
            measured_power = float(input("Please enter the measured power (e.g. 40)"))
            if not 10 <= measured_power <= 120:
                print("Bad value")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid number for measured power.")

    while True:
        try:
            n = int(input("Please enter a number for n (e.g. 2): "))
            if not 1 <= n <= 4:
                print("n must be between 1 and 4.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer for n.")

    mon_interface = input("Please enter the network interface for monitor mode: (e.g. wlan1mon) ")
       


    probelist = []
    all_received_probes = []
    common_queue = []
    devices = []
    sniffercords = [None]
    if run_radar == "y":
        sniffercords_ready = threading.Event()
    else:
        sniffercords_ready = None
        sniffercords[0] = {'x': x, 'y': y}
    lock = threading.Lock()

    interface = "wlan1"
    monitor_interface = setup_interface.setup_interface(interface, mon_interface)
    


    def get_unique_ip(base):

        # Get the MAC address of wlan0 to generate a unique IP

        result = subprocess.run(['cat', '/sys/class/net/wlan0/address'], stdout=subprocess.PIPE)

        mac = result.stdout.decode('utf-8').strip()

        unique_suffix = int(mac.split(':')[-1], 16) % 254 + 1  # Using last byte of MAC address for uniqueness

        return f"{base}{unique_suffix}"

 

    def configure_adhoc_network():

        # Stop interfering services

        os.system('sudo systemctl stop NetworkManager')

        os.system('sudo systemctl stop wpa_supplicant')

        os.system('sudo ifconfig wlan0 down')

        os.system('sudo iwconfig wlan0 mode ad-hoc')

        os.system('sudo iwconfig wlan0 essid "YourAdHocSSID"')

        os.system('sudo iwconfig wlan0 channel 1')

        # Assign unique IP based on MAC address

        unique_ip = get_unique_ip('10.192.200.')

        os.system(f'sudo ifconfig wlan0 {unique_ip} netmask 255.255.0.0')

        os.system('sudo ifconfig wlan0 up')

        return unique_ip

    

    def configure_socket(interface_ip):

        # Bind a socket to the interface IP and a specific port for UDP communication

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.bind((interface_ip, 12345))

        return sock

    

    def send_data(sock, network_ips):
        while True:
            random_value = random.randint(1000, 9999)
            for ip in network_ips:
                sock.sendto(f"Random value {random_value}".encode(), (ip, 12345))
            time.sleep(5)

    

    def receive_data(sock):

        while True:

            data, addr = sock.recvfrom(1024)

            print(f"These values {data.decode()} are from {addr[0]}")



    
    my_ip = configure_adhoc_network()

    sock = configure_socket(my_ip)

    network_ips = [f"10.192.200.{i}" for i in range(1, 255) if f"10.192.200.{i}" != my_ip]


    sniff_thread = threading.Thread(target=packet_sniffer,
                                     args=(monitor_interface, probelist, sniffercords, lock, sniffercords_ready, measured_power, n), daemon=False)
    
    
    receive_data_thread = threading.Thread(target=receive_data, args=(sock,), daemon=True)
    
    
    send_thread = threading.Thread(target=send_data, args=(sock, network_ips), daemon=True)
    
    sync_probes_thread = threading.Thread(target=sync_probes,
                                     args=(probelist, all_received_probes, common_queue, lock), daemon=False)

    update_thread = threading.Thread(target=update,
                                    args=(common_queue, devices, lock), daemon=False)
    if to_run > 0:   
        sniff_thread.start()
    if to_run > 1:
        print(f"[main]\tStarting broadcast thread with args: sock={sock}, network_ips={network_ips}, probelist={probelist}, ")
        send_thread.start()
    if to_run > 2:
        print(f"[main]\tStarting receive_probes_thread with args: sock={sock}, all_received_probes={all_received_probes}")
        receive_data_thread.start()
    if to_run > 3:
        print(f"[main]\tStarting sync_probes_thread with args: probelist={probelist}, all_received_probes={all_received_probes}, 
              common_queue={common_queue}, lock={lock}")
        sync_probes_thread.start()
    if to_run > 4:
        print(f"[main]\tStarting update_thread with args: common_queue={common_queue}, devices={devices}, 
              lock={lock}")
        update_thread.start()
    if run_radar == "y":    
        print(f"[main]\tStarting radar  with args: devices={devices}, sniffercords={sniffercords}, sniffercords_ready={sniffercords_ready}, ")
        radar.radar_main(devices, sniffercords, sniffercords_ready)






if __name__ == "__main__":

    print("[Main] Starting program")
    print("[Main] Starting program")
    print("[Main] Starting program")

    run()
    


















