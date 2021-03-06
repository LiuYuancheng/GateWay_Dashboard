#-----------------------------------------------------------------------------
# Name:        gwLatClient.py
#
# Purpose:     This module is used as Client to check the Latency from the computer
#              to the host(IPv4/domain), then report to the server to calculate
#              the latency generated by the encryption device.
# 
# Author:      Yuancheng Liu
#
# Created:     2019/12/06
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import socket
import sys
import time
from statistics import mean

# tcp_latency: https://pypi.org/project/tcp-latency/#similar-tools
from tcp_latency import measure_latency

GW_ID = 'GW_00' # gateway ID
SEV_IP = ('127.0.0.1', 5010)    # The server's IP address.
IN_FLG = 'I'  # flag to identify whether the device is "behind" encryption device.
BUFFER_SZ = 1024
LAT_HOST = 'www.google.com'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    terminate = False
    gwUdpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # login to the server.
    loginStr = ';'.join(('L', GW_ID, IN_FLG, '0','-1'))
    gwUdpClient.sendto(loginStr.encode('utf-8'), SEV_IP)
    while not terminate:
        data, _ = gwUdpClient.recvfrom(BUFFER_SZ)
        if not data: break
        if isinstance(data, bytes):
            msg = data.decode(encoding="utf-8")
            print('Received msg %s' %msg)
            if 'L' in msg:
                cIdx = msg.split(';')[1]
                latency = mean(measure_latency(host='google.com'))
                respStr = ';'.join(('L', GW_ID, IN_FLG, cIdx, str(latency)))
                gwUdpClient.sendto(respStr.encode('utf-8'), SEV_IP)
                print(respStr)

if __name__== "__main__":
    main()