import socket
import threading
import Queue
import random
import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

DEFAULT_TIMEOUT = None
IP_ADDRESS = 'localhost'
FILEPATH = 'C:/Users/aakab_000/PycharmProjects/Assignment2/Data/'
TIME_OF_RUN = 60
EVENT_NUM = 10

class VM(threading.Thread):
    def __init__(self, clockspeed, selfport, vm1port, vm2port):
        self.LC = 0
        self.queue = Queue.Queue()
        self.sst = threading.Thread(target = server_socket_thread, args=(selfport, self.queue))
        self.sst.daemon = True
        self.sst.start()
        self.selfport = selfport
        self.vm1port = vm1port
        self.vm2port = vm2port
        self.clockspeed = clockspeed
        self.filepath = FILEPATH + str(selfport) + '.txt'
        print(self.filepath)
        with open(self.filepath, 'w') as file_:
            file_.write('system time\tLC\top\tqsize\treceived from\n')
        threading.Thread.__init__(self)


    def run(self):
        initial_time = datetime.datetime.now()
        cycletime = 1.0/self.clockspeed
        cycle_start_time = datetime.datetime.now()
        while((cycle_start_time-initial_time).total_seconds() < TIME_OF_RUN):
            if self.queue.empty():
                op = random.randint(1,EVENT_NUM)
                if op == 1:
                    cst = threading.Thread(target = client_socket_thread, args = (self.vm1port, str(self.selfport) + ' ' + str(self.LC)))
                    cst.start()
                elif op == 2:
                    cst = threading.Thread(target = client_socket_thread, args = (self.vm2port, str(self.selfport) + ' ' + str(self.LC)))
                    cst.start()
                elif op == 3:
                    cst1 = threading.Thread(target = client_socket_thread, args = (self.vm1port, str(self.selfport) + ' ' + str(self.LC)))
                    cst1.start()
                    cst2 = threading.Thread(target = client_socket_thread, args = (self.vm2port, str(self.selfport) + ' ' + str(self.LC)))
                    cst2.start()
                self.LC += 1
                sender = 0
            else:
                op = 0
                msg = self.queue.get()
                sender = msg.split()[0]
                LC_received = int(msg.split()[1])
                LC = max(LC_received + 1, self.LC + 1)
            with open(self.filepath, 'a') as file_:
                file_.write(str(cycle_start_time.time())+'\t' + str(self.LC) + '\t' + str(op) + '\t' + str(self.queue.qsize()) + '\t' + str(sender) + '\n')
            time.sleep(cycletime - (datetime.datetime.now() - cycle_start_time).total_seconds())
            cycle_start_time = datetime.datetime.now()

def server_socket_thread(port, queue):
    socket.setdefaulttimeout(DEFAULT_TIMEOUT)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((IP_ADDRESS, port))
    serversocket.listen(5)
    queue = queue
    while(True):
        clientsocket, _ = serversocket.accept()
        msg = clientsocket.recv(4096)
        if msg == '':
            raise RuntimeError("socket connection broken")
        queue.put(msg)
        clientsocket.close()

def client_socket_thread(target_port, msg):
    socket.setdefaulttimeout(DEFAULT_TIMEOUT)
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_port = target_port
    clientsocket.connect((IP_ADDRESS, target_port))
    sent = clientsocket.send(msg)
    if sent == 0:
        raise RuntimeError("socket connection broken")
    clientsocket.close()

def run_vm(port1, port2, port3):
    vm1port = port1
    vm2port = port2
    vm3port = port3
    vm1 = VM(random.randint(1,6), vm1port, vm2port, vm3port)
    vm2 = VM(random.randint(1,6), vm2port, vm1port, vm3port)
    vm3 = VM(random.randint(1,6), vm3port, vm1port, vm2port)
    #vm1 = VM(1, vm1port, vm2port, vm3port)
    #vm2 = VM(100, vm2port, vm1port, vm3port)
    #vm3 = VM(100, vm3port, vm1port, vm2port)

    vm1.start()
    vm2.start()
    vm3.start()

def analyze(filepaths):
    figure1 = plt.figure()
    ax1 = figure1.add_subplot(111)
    figure2 = plt.figure()
    ax2 = figure2.add_subplot(111)
    figure3 = plt.figure()
    ax3 = figure3.add_subplot(111)
    for f in filepaths:
        a = pd.read_table(f)
        times = a.values[:,0]
        for n in range(0,len(times)):
            times[n] = datetime.datetime.strptime(times[n], "%H:%M:%S.%f")
        LC = a.values[:,1]
        ax1.plot_date(times,LC, '-')
        deltaLC = np.diff(LC)
        deltaLC = np.insert(deltaLC,0,1)
        ax3.plot_date(times,deltaLC)
        qsize = a.values[:,3]
        ax2.plot_date(times,qsize,'-')
    plt.show()

if __name__ == '__main__':
    run_vm(1000,1001,1002)
    #filepaths = ['C:/Users/aakab_000/PycharmProjects/Assignment2/Data/1000.txt', 'C:/Users/aakab_000/PycharmProjects/Assignment2/Data/1001.txt', 'C:/Users/aakab_000/PycharmProjects/Assignment2/Data/1002.txt']
    #analyze(filepaths)
