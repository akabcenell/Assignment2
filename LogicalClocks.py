import socket
import threading
import Queue
import random
import datetime
DEFAULT_TIMEOUT = None
IP_ADDRESS = 'localhost'
FILEPATH = 'C:/Users/aakab_000/PycharmProjects/Assignment2/Data/'

class VM(threading.Thread):
    def __init__(self, clockspeed, selfport, vm1port, vm2port):
        self.LC = [0]
        self.queue = Queue.Queue()
        self.sst = threading.Thread(target = server_socket_thread, args=(selfport, self.queue))
        self.sst.start()
        self.selfport = selfport
        self.vm1port = vm1port
        self.vm2port = vm2port
        self.clockspeed = clockspeed
        self.filepath = FILEPATH + str(selfport) + '.txt'
        print(self.filepath)
        with open(self.filepath, 'w') as file_:
            file_.write('system time\tlogical clock time\toperation\tqueue size\treceived from\n')
        print('here' + str(self.selfport))
        threading.Thread.__init__(self)


    def run(self):
        threading.Timer((1.0/self.clockspeed), clock_cycle, args = (self.queue, self.selfport, self.vm1port, self.vm2port, self.LC, self.filepath, self.clockspeed)).start()

def clock_cycle(queue, selfport, vm1port, vm2port, LC, filepath, clockspeed):
    threading.Timer((1.0/clockspeed), clock_cycle, args = (queue, selfport, vm1port, vm2port, LC, filepath, clockspeed)).start()
    if queue.empty():
        op = random.randint(1,10)
        if op == 1:
            cst = threading.Thread(target = client_socket_thread, args = (vm1port, str(selfport) + ' ' + str(LC[0])))
            cst.start()
        elif op == 2:
            cst = threading.Thread(target = client_socket_thread, args = (vm2port, str(selfport) + ' ' + str(LC[0])))
            cst.start()
        elif op == 3:
            cst1 = threading.Thread(target = client_socket_thread, args = (vm1port, str(selfport) + ' ' + str(LC[0])))
            cst1.start()
            cst2 = threading.Thread(target = client_socket_thread, args = (vm2port, str(selfport) + ' ' + str(LC[0])))
            cst2.start()
        LC[0] = LC[0] + 1
        sender = 0
    else:
        op = 0
        msg = queue.get()
        sender = msg.split()[0]
        LC_received = int(msg.split()[1])
        LC[0] = max(LC_received + 1, LC[0] + 1)
    print('here' + str(selfport))
    with open(filepath, 'a') as file_:
        file_.write(str(datetime.datetime.now())+'\t' + str(LC[0]) + '\t' + str(op) + '\t' + str(queue.qsize()) + '\t' + str(sender) + '\n')

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

vm1port = 1025
vm2port = 1026
vm3port = 1027
vm1 = VM(random.randint(1,6), vm1port, vm2port, vm3port)
vm2 = VM(random.randint(1,6), vm2port, vm1port, vm3port)
vm3 = VM(random.randint(1,6), vm3port, vm1port, vm2port)

vm1.start()
vm2.start()
vm3.start()
