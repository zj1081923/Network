import sys
from socket import *
import time
import pickle
import random

"Use this method to write Packet log"


def writePkt(logFile, procTime, pktNum, event):
    if pktNum > 0:
        logFile.write('{:1.3f} pkt: {} | {}'.format(procTime, pktNum-1, event))


"Use this method to write ACK log"


def writeAck(logFile, procTime, ackNum, event):
    if ackNum > 0:
        logFile.write('{:1.3f} ACK: {} | {}'.format(procTime, ackNum-1, event))


"Use this method to write final throughput log"


def writeEnd(logFile, throughput):
    logFile.write('File transfer is finished. \n')
    logFile.write('Goodput : {:.2f} pkts/sec'.format(throughput))

class Packet:
    def __init__(self, seq, data):
        self.seq = seq
        self.data = data
    def set_sentTime(self):
        self.sentTime = time.time()

class RecvInfo:
    def __init__(self, recvAddr):
        self.recvAddr = recvAddr
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(recvAddr)

def fileReceiver(recvinfo):


    in_order = -1
    buffer = {}
    check = False

    while in_order < 0:
        metadata, senderip = recvinfo.sock.recvfrom(1400)
        metadata = pickle.loads(metadata)
        if metadata.seq == 0:
            in_order += 1
            dstFilename = metadata.data.split(':')[0]
            total_pkt = int(metadata.data.split(':')[1])
            recvinfo.sock.sendto(str(in_order).encode(), senderip)
            break
        else:
            recvinfo.sock.sendto(str(in_order).encode(), senderip)
    #print(dstFilename)
    #print(total_pkt)


    checkrecv = [False] * (total_pkt+1)
    checkrecv[0] = True

    f = open(dstFilename + "_receiving_log.txt", "w")
    target_f = open(dstFilename, "wb+")

    startTime = time.time()

    while in_order < total_pkt:
        pkt, _ = recvinfo.sock.recvfrom(1400)
        pkt = pickle.loads(pkt)


        writePkt(f, time.time()-startTime, pkt.seq, "received\n")
        if pkt.seq == in_order + 1:
            in_order += 1
            checkrecv[pkt.seq] = True
            target_f.write(pkt.data)

            if in_order == total_pkt:
                recvinfo.sock.sendto(str(in_order).encode(), senderip)
                writeAck(f, time.time()-startTime, pkt.seq, "sent\n")
                break
            while checkrecv[in_order + 1]:
                in_order += 1
                target_f.write(buffer[in_order])
                buffer.pop(in_order)
                if in_order == total_pkt:
                    break
        else:
            checkrecv[pkt.seq] = True
            buffer[pkt.seq] = pkt.data
        recvinfo.sock.sendto(str(in_order).encode(), senderip)
        if in_order == total_pkt:
            recvinfo.sock.sendto(str(in_order).encode(),senderip)
        writeAck(f, time.time()-startTime, in_order, "sent\n")

    writeEnd(f, total_pkt/(time.time()-startTime))
    f.close()
    target_f.close()

    FIN_signal(recvinfo, in_order, total_pkt, senderip)

def FIN_signal(recvinfo, in_order, total_pkt, senderip): # in_order == total_pkt
    while in_order < total_pkt+1:
        pkt, _ = recvinfo.sock.recvfrom(1400)
        pkt = pickle.loads(pkt)
        if pkt.seq == total_pkt + 1:
            in_order += 1
            recvinfo.sock.sendto(str(in_order).encode(), senderip)
            #print("send "+str(in_order))
            break
        else:
            recvinfo.sock.sendto(str(in_order).encode(), senderip)
            #print("send again: "+str(in_order))


if __name__ == '__main__':
    recvinfo = RecvInfo(("", 10080))
    fileReceiver(recvinfo)