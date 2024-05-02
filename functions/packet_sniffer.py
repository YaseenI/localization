from scapy.all import sniff
from functions import process_packet

def packet_sniffer(interface, probelist, sniffercords, lock, sniffercords_ready):
        if sniffercords_ready != None: 
                sniffercords_ready.wait()
        print(f"[Startup] [Packet_sniffer()]    Executing sniff(iface={interface}, prn=lambda packet: process_packet.process_packet(packet, probelist={probelist}, sniffercords={sniffercords}, lock={lock}), store=False, lfilter=lambda x: x.type == 0 and x.subtype == 4)") 
        sniff(iface=interface, prn=lambda packet: process_packet.process_packet(packet, probelist, sniffercords, lock), store=False, lfilter=lambda x: x.type == 0 and x.subtype == 4)
