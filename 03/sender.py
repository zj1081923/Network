import sys
import socket
from threading import *
import math
import os
import time
import pickle

"Use this method to write Packet log"


def writePkt(logFile, procTime, pktNum, event):
    if pktNum > 0:
        logFile.write('{:1.3f} pkt: {} | {}'.format(procTime, pktNum-1, event))


"Use this method to write ACK log"


def writeAck(logFile, procTime, ackNum, event):
    if ackNum > 0:
        logFile.write('{:1.3f} ACK: {} | {}'.format(procTime, ackNum-1, event))


"Use this method to write final throughput log"


def writeEnd(logFile, throughput, avgRTT):
    logFile.write('File transfer is finished. \n')
    logFile.write('Goodput : {:.2f} pkts/sec \n'.format(throughput))
    logFile.write('Average RTT : {:.1f} ms'.format(avgRTT * 1000))


class SendInfo:
    def __init__(self, recvAddr, windowSize, timeout, srcFilename, dstFilename):
        self.recvAddr = recvAddr
        self.winSize = windowSize
        self.timeout = timeout
        self.srcFilename = srcFilename
        self.dstFilename = dstFilename
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0))
        self.sock.settimeout(5)
        self.lock = Lock()
        self.devRTT = -1
        self.avgRTT = -1
        self.in_order = -1
        self.duplicate = 0
        self.closed = False
        #print("Sender init is done..")

    def init_startTime(self):
        self.startTime = time.time()

    def init_sentpkt(self, total_pkt):
        self.sentpkt = []  # class pkt 저장
        self.checksend = [False] * (total_pkt+1)


class Packet:
    def __init__(self, seq, data):
        self.seq = seq
        self.data = data

    def set_sentTime(self):
        self.sentTime = time.time()


def calculate_RTT(sampleRTT, sendinfo):
    if sendinfo.avgRTT < 0:
        sendinfo.avgRTT = sampleRTT
        sendinfo.devRTT = 0.5 * sampleRTT
    else:
        sendinfo.avgRTT = 0.875 * sendinfo.avgRTT + 0.125 * sampleRTT
        sendinfo.devRTT = 0.75 * sendinfo.devRTT + 0.25 * abs(sampleRTT - sendinfo.avgRTT)

    sendinfo.timeout = min(sendinfo.avgRTT + 4 * sendinfo.devRTT, 60)


def recvAck(f, total_pkt, sendinfo):
    while sendinfo.in_order < total_pkt+1:
        try:
            ack, _ = sendinfo.sock.recvfrom(100)
            ack = int(ack.decode())
        except socket.timeout:
            continue
        curtime = time.time()

        if sendinfo.closed == False:
            writeAck(f, curtime - sendinfo.startTime, ack, "received\n")
            if ack == total_pkt:
                sendinfo.closed = True

        if ack == sendinfo.in_order + 1:
            with sendinfo.lock:
                sendinfo.in_order += 1
                sendinfo.duplicate = 0
                try:
                    calculate_RTT(curtime-sendinfo.sentpkt[ack].sentTime, sendinfo)
                except IndexError:
                    pass

        elif ack < sendinfo.in_order:
            continue

        elif ack == sendinfo.in_order:
            with sendinfo.lock:
                sendinfo.duplicate += 1
        else:
            with sendinfo.lock:
                sendinfo.in_order = ack
                sendinfo.duplicate = 0


def fileSender(sendinfo):


    total_pkt = math.ceil(os.path.getsize(sendinfo.srcFilename) / 1300)
    metamsg = sendinfo.dstFilename + ":{}".format(total_pkt)
    final_pkt = total_pkt
    f = open(sendinfo.srcFilename + "_sending_log.txt", "w")
    target_f = open(sendinfo.srcFilename, "rb")

    recvack = Thread(target=recvAck, args=(f, total_pkt, sendinfo))
    recvack.start()

    sendinfo.init_sentpkt(total_pkt)
    start = False
    sendinfo.init_startTime()

    while sendinfo.in_order < total_pkt:
        if sendinfo.in_order == -1:
            limit = 1
        else:
            limit = min(sendinfo.in_order + 1 + sendinfo.winSize, total_pkt+1)
            if start == False:
                start = True
                sendinfo.init_startTime()
        for i in range(sendinfo.in_order + 1, limit):
            if sendinfo.checksend[i] == False:
                if sendinfo.in_order == -1:
                    pkt = Packet(0, metamsg)
                else:
                    d = target_f.read(1300)
                    pkt = Packet(i, d)
                pkt.set_sentTime()
                sendinfo.sock.sendto(pickle.dumps(pkt), sendinfo.recvAddr)
                sendinfo.sentpkt.append(pkt)
                sendinfo.checksend[i] = True
                writePkt(f, time.time() - sendinfo.startTime, i, "sent\n")

        with sendinfo.lock:
            if sendinfo.in_order < total_pkt:
                if sendinfo.checksend[sendinfo.in_order + 1] == True:
                    if time.time() - sendinfo.sentpkt[sendinfo.in_order + 1].sentTime > sendinfo.timeout:

                        try:

                            pkt = sendinfo.sentpkt[sendinfo.in_order + 1]
                            writePkt(f, time.time() - sendinfo.startTime, sendinfo.in_order + 1, str(
                                'timeout since {:1.3f} (timeout value {:1.3f})\n'.format(
                                    pkt.sentTime - sendinfo.startTime, sendinfo.timeout)))
                        except IndexError:
                            continue

                        final_pkt += 1
                        sendinfo.sock.sendto(pickle.dumps(pkt), sendinfo.recvAddr)
                        writePkt(f, time.time() - sendinfo.startTime, sendinfo.in_order + 1, "retransmitted\n")

                        before_sentTime = pkt.sentTime
                        sendinfo.sentpkt[sendinfo.in_order + 1].set_sentTime()

                        sendinfo.duplicate = 0
                        continue
        with sendinfo.lock:
            if sendinfo.duplicate >= 3:
                writePkt(f, time.time() - sendinfo.startTime, sendinfo.in_order, "3 duplicated Acks\n")
                try:
                    pkt = sendinfo.sentpkt[sendinfo.in_order + 1]
                except IndexError:
                    continue
                final_pkt += 1
                sendinfo.sock.sendto(pickle.dumps(pkt), sendinfo.recvAddr)
                writePkt(f, time.time() - sendinfo.startTime, sendinfo.in_order + 1, "retransmitted\n")

                sendinfo.sentpkt[sendinfo.in_order + 1].set_sentTime()
                sendinfo.duplicate = 0
    goodput = total_pkt / (time.time() - sendinfo.startTime)
    writeEnd(f, goodput, sendinfo.avgRTT)


    f.close()
    target_f.close()

    pkt = Packet(total_pkt+1, "")
    FIN_sent = time.time()

    sendinfo.sock.sendto(pickle.dumps(pkt), sendinfo.recvAddr)

    while sendinfo.in_order < total_pkt+1:
        if time.time() - FIN_sent > sendinfo.timeout:
            sendinfo.in_order = total_pkt+1
            break





if __name__ == '__main__':
    recvAddr = sys.argv[1]  # receiver IP address
    windowSize = int(sys.argv[2])  # window size
    srcFilename = sys.argv[3]  # source file name
    dstFilename = sys.argv[4]  # result file name

    sendinfo = SendInfo((recvAddr, 10080), windowSize, 1, srcFilename, dstFilename)
    fileSender(sendinfo)