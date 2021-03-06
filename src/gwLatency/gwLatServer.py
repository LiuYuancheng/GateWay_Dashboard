#-----------------------------------------------------------------------------
# Name:        gwLatServer.py
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
import threading

SEV_IP = ('0.0.0.0', 5010)
BUFFER_SZ = 1024

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class RespSer(threading.Thread):
    """ Client FB UDP reading server thread.""" 
    def __init__(self, threadID, name, parent):
        threading.Thread.__init__(self)
        # Init drone feed back data list.
        self.parent = parent
        self.terminate = False
        self.udpSer = self.parent.sock

#--telloRespSer----------------------------------------------------------------
    def run(self):
        """ main loop to handle the data feed back."""
        while not self.terminate:
            data, address = self.udpSer.recvfrom(BUFFER_SZ)
            if not data: break
            if isinstance(data, bytes):
                dataStr = data.decode(encoding="utf-8")
                msgList = dataStr.split(';')
                self.parent.updateGWData(msgList, address)

#--telloRespSer----------------------------------------------------------------
    def stop(self):
        """ Send back a None message to terminate the buffer reading waiting part."""
        self.terminate = True
        closeClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        closeClient.sendto(b'', ("127.0.0.1", SEV_IP[1]))
        closeClient.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class gwLatServer(object):

    def __init__(self, parent):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.terminate = False
        self.sock.bind(SEV_IP)
        self.simulation = False
        self.gatewayDict = {}   #name:[ipIn, ipOut, latnIn latnOut]
        self.droneRsp = RespSer(0, "Latency Server", self)
        self.droneRsp.start()

#-----------------------------------------------------------------------------
    def updateGWData(self, msgList, ipaddr):
        if len(msgList) != 5: return
        print("> %s" %str(msgList))
        tag, gwId, inFg, idx, lat = msgList
        latKey = 'latnIn' if inFg == 'I' else 'latOut'
        if gwId in self.gatewayDict.keys():
            # update the record
            print
            self.gatewayDict[gwId][latKey] = float(lat)
        else:
            # Add new gateway inside
            gwDict = {'ipIn': ('127.0.0.1',SEV_IP[1]),
                      'ipOut':('127.0.0.1',SEV_IP[1]),
                      'latnIn': 1.0,
                      'latnOut': 0.0
                      }
            ipKey = 'ipIn' if inFg == 'I' else 'ipOut'
            gwDict[ipKey] = ipaddr
            print(lat)
            gwDict[latKey] = float(lat)
            self.gatewayDict[gwId] = gwDict
        print(">> %s" %str(self.gatewayDict))

    def startSev(self):
        print('Server started')
        while not self.terminate:
            print(self.gatewayDict)
            # send the ping check command
            for key in self.gatewayDict.keys():
                dataDict = self.gatewayDict[key]
                # send to the inside client
                ipaddrIn = dataDict['ipIn']
                respStr = ';'.join(('L', '0'))
                self.sock.sendto(respStr.encode('utf-8'), ipaddrIn)

                ipaddrOut = dataDict['ipOut']
                respStr = ';'.join(('L', '0'))
                self.sock.sendto(respStr.encode('utf-8'), ipaddrOut)
            time.sleep(5)

#-----------------------------------------------------------------------------
def serverRun():
    serv = gwLatServer(None)
    serv.startSev()
	
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    serverRun()

