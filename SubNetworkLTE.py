#============== Python3 Flask Model of LTE Sub Network ==============
#   Version: 1.00
#   Monty Dimkpa

from flask import Flask, request
from flask_cors import CORS
import sys
import os
import pickle
from random import random
import datetime
from hashlib import md5

app = Flask(__name__)
CORS(app)

#-------------- Network Initialization Parameters --------------

server_host, server_port = sys.argv[1:]

NETWORK_HOME = os.getcwd()
if "\\" in NETWORK_HOME:
    slash = "\\"
else:
    slash = "/"
NETWORK_HOME+=slash

#-------------- Network Constants ------

default_MAC_packet_size = 1500  # default MAC packet size (MTU) of 1.5 KB for LTE
min_IP_packet_size = 1000
max_IP_packet_size = 5000

#-------------- Base Classes --------------

def Path(path_array):
    return slash.join(path_array)

def now(): return datetime.datetime.today()

def ms_elapsed(t): return int(1000*(now() - t).total_seconds())

def Id():
    hasher = md5(); hasher.update(str(now()).encode())
    return hasher.hexdigest()

class IP_Packet:
    def __init__(self, sessionId, size, source, time):
        self.sessionId = sessionId
        self.header = [size, source, time]
        self.payload_bits = "".join([str(int(random()*2)) for i in range(size)]).encode()
    def loggable(self):
        return pickle.dumps(self)

class MAC_Packet:
    def __init__(self, sessionId, bits, source, delay):
        self.sessionId = sessionId
        self.header = [delay, source, now()]
        self.payload_bits = bits
    def loggable(self):
        return pickle.dumps(self)

def split_bits_by_plan(bits, plan):
    field = [x for x in bits.decode()]
    bands = []
    for size in plan:
        sub = []
        for i in range(size):
            sub.append(field.pop())
        bands.append("".join(sub).encode())
    return bands

def split_into(x, b):
    divs = x // b
    rem = x % b
    if divs:
        if rem:
            return [b for i in range(divs)]+[rem]
        else:
            return [b for i in range(divs)]
    else:
        return [x]

def packet_size():
    return int(min_IP_packet_size + random()*(max_IP_packet_size - min_IP_packet_size))

def UESession(ip_address, n_packets):
    sessionId = Id()
    session_time = now()
    return [ip_address, session_time, sessionId, n_packets, [IP_Packet(sessionId, packet_size(), ip_address, session_time).loggable() for i in range(n_packets)]]
    
class NetworkDataManager:
    def __init__(self, net_cookie_host_dir):
        self.net_cookie_path = [NETWORK_HOME, net_cookie_host_dir]
        try:
            os.mkdir(Path(self.net_cookie_path))
        except:
            pass
        self.net_cookies = {}
    def register_new_net_cookie(self, net_cookie_type):
        self.net_cookies[net_cookie_type] = Path(self.net_cookie_path+["%s.net_cookie" % net_cookie_type])
    def write_net_cookie(self, net_cookie_type, data):
        if net_cookie_type not in self.net_cookies:
            self.register_new_net_cookie(net_cookie_type)
        p = open(self.net_cookies[net_cookie_type], "wb+")
        p.write(repr(data).encode())
        p.close()
        return data
    def read_net_cookie(self, net_cookie_type):
        if net_cookie_type in self.net_cookies:
            p = open(self.net_cookies[net_cookie_type], "rb+")
            data = eval(p.read().decode())
            p.close()
            return data
        else:
            return None

def log(sessionId, request, response):
    def format():
        colorMap = {"IP_PACKETS_RECEIVED":"yellow", "MAC_PACKETS_MODULATED":"cyan"}
        return str(now()), sessionId, colorMap[request], request, response
    Log = NetLog.read_net_cookie("log")
    if Log:
        Log.append(format())
    else:
        Log = [format()]
    NetLog.write_net_cookie("log", Log)
    return None

#-------------- Component Data Models --------------

AirInterface = NetworkDataManager("AirInterface")
PhysicalUplinkControlChannel = NetworkDataManager("PhysicalUplinkControlChannel")
MAC = NetworkDataManager("MAC")
MAC.write_net_cookie("MAC_packet_size", default_MAC_packet_size)
Scheduler = NetworkDataManager("Scheduler")
Transmission = NetworkDataManager("Transmission")
NetLog = NetworkDataManager("NetLog")

#-------------- Network Endpoints --------------

@app.route("/SubNetworkLTE/NetLog")
def ShowActivity():
    Log = NetLog.read_net_cookie("log")
    if Log:
        html = '<html><body bgcolor="black"><div style="color: white; font-family: consolas; font-size:12;">%s</div></body></html>'
        spool = ""; count = -1
        for log in Log[::-1]:
            count+=1
            spool += '<p><b>%s --> </b>[%s] <span style="color: %s;">[%s]</span> [%s]' % log + ' (#%s)</p>' % str(len(Log) - count)
        return html % spool
    else:
        return "%s: %s" % (404, "No activity logs found")

@app.route("/SubNetworkLTE/PhysicalUplinkControlChannel/Modulation")
def ModulatePackets():
    UERegister = AirInterface.read_net_cookie("UERegister")
    session = None
    try:
        session = UERegister.pop()
        AirInterface.write_net_cookie("UERegister", UERegister)
    except:
        pass
    if session:
        ip_address, session_time, sessionId, n_packets, ip_packets_loggable = session
        ip_packets = [pickle.loads(log) for log in ip_packets_loggable]
        # Packet Modulation
        MAC_packets = []
        MAC_packet_size = MAC.read_net_cookie("MAC_packet_size")
        delay = ms_elapsed(session_time)
        for packet in ip_packets:
            field = split_bits_by_plan(packet.payload_bits, split_into(packet.header[0], MAC_packet_size))
            for bits in field:
                MAC_packets.insert(0, MAC_Packet(sessionId, bits, ip_address, delay).loggable()) # FIFO Queue
        QueuedMACPackets = PhysicalUplinkControlChannel.read_net_cookie("QueuedMACPackets")
        if QueuedMACPackets:
            QueuedMACPackets += MAC_packets
        else:
            QueuedMACPackets = MAC_packets
        PhysicalUplinkControlChannel.write_net_cookie("QueuedMACPackets", QueuedMACPackets)
        log(sessionId, "MAC_PACKETS_MODULATED", "%s MAC packets from %s IP packets sent by %s delayed %sms" % (len(MAC_packets), n_packets, ip_address, delay))
        return "%s: %s" % (200, "Successfully modulated %s packets" % len(MAC_packets))
    else:
        return "%s: %s" % (404, "No session found")

@app.route("/SubNetworkLTE/AirInterface/UERegistration/<path:n_packets>")
def UERegistration(n_packets):
    ip_address = request.remote_addr
    try:
        session = UESession(ip_address, int(n_packets))
    except:
        return "%s: %s" % (400, "Error creating session: packet_size not specified")
    UERegister = AirInterface.read_net_cookie("UERegister")
    if UERegister:
        UERegister.insert(0, session)  #FIFO Queue
    else:
        UERegister = [session]
    AirInterface.write_net_cookie("UERegister", UERegister)
    log(session[2], "IP_PACKETS_RECEIVED", "UE sent %s packets of %s bytes from %s" % (n_packets, sum([pickle.loads(loggable).header[0] for loggable in session[4]]), ip_address))
    return "%s: %s" % (200, "Successfully registered %s packets" % n_packets)

if __name__ == "__main__":
    app.run(host=server_host, port=server_port, threaded=True)
