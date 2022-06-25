import socket
import select
import struct
import multiprocessing

import simulator


LOCK = 0
R_LOCK = 1

class Worker(object):
    
    def __init__(self, sock, name, address) -> None:
        self.name = name
        self.sock = sock
        self.pid = None
        self.timeout = 9999
        self.lock = LOCK
        self.worker_sock = self.create_sock(address)
        self.master_sock = None

    @staticmethod
    def create_sock(address):
        """ 创建与master通信的socket
        Args: address: ip端口号 例子: ("127.0.0.1", 8888)

        Return: socket对象
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(address)
        sock.listen(10000)
        return sock

    def run(self):
        """ woker进程

            主要负责与 master通信(如果空闲会给master通信，并且告诉当前read_list的监听数量)
            和 解析收到客户端的请求数据包内容、执行操作。
 
        """
        read_list = []
        client, _, _ = select.select([self.worker_sock], [], [], 100)

        if client:
            cli, _ = self.worker_sock.accept()
            self.master_sock = cli
            read_list.append(self.master_sock)
        
        while True:
            if read_list:
                length = len(read_list)
                self.master_sock.send(str(length).encode())

                r_l, _, _ = select.select(read_list, [], [], self.timeout)

                for fd in r_l:
                    if fd == self.master_sock:
                        g = self.master_sock.recv(1)

                        if g == b'1':
                            c, _ = self.sock.accept()
                            read_list.append(c)
                            print("new client arrive", self.name)
                    else:
                        # 接收数据
                        f = fd.recv(300)
                        if f:
                            result = exec(f)
                            # head = int.from_bytes(f[0:4],byteorder='big')
                            # typ = eval(f[4:])[0]
                            # id = eval(f[4:])[1]
                            # content = eval(f[4:])[2]
                            # print("client %s request: len-%s type-%s id-%s content-%s" % (self.name, head, typ, id, content))
                            # print("client %s request:%s" % (self.name, f.decode('gbk')))

                        else:
                            print("client %s close" % str(self.name))
                            read_list.remove(fd)
                            fd.close()
    def make_worker(self):
        """启动一个worker子进程
        """
        return multiprocessing.Process(name="worker_"+str(self.name), target=self.run)

    def exec(data):
        head = int.from_bytes(data[0:4],byteorder='big')
        typ = eval(data[4:])[0]
        sid = eval(data[4:])[1]
        content = eval(data[4:])[2]

        msgid = 0
        result = ''
        get_method = content[0]

        if get_method == 'init':
            """init(self, sid, **sim_params)"""
            sid = content[1][0]
            kwargs = content[1][-1]
            result = simulator.Simulator.init(sid, kwargs)

        elif get_method == 'create':
            """create(self, num, model, **model_params)"""
            num = content[1][0]
            model = content[1][1]
            kwargs = content[1][-1]
            simulator.Simulator.create(num, model, kwargs)
            

        elif get_method == 'setup_done':
            """setup_done(self)"""
            simulator.Simulator.setup_done()
            

        elif get_method == 'step':
            """step(self, time, inputs)"""
            time = content[1][0]
            inputs = content[1][1]
            simulator.Simulator.step(time)
            

        elif get_method == 'get_data':
            """get_data(self, outputs)"""
            outputs = content[1][0]
            simulator.Simulator.get_data(outputs)
            

        elif get_method == 'finalize':
            """finalize(self)"""
            simulator.Simulator.finalize()


        else:
            msgid = 2
            result = "Error in your code"
        Worker.reply_msg(msgid, sid, result)

    def reply_msg(msgid, sid, result):
        rep = []
        req_msg_id = sid
        rep.append(msgid)
        rep.append(req_msg_id)
        rep.append(result)
        length = struct.pack('>i',len(rep))
        msg = str(length)+str(rep)
        return msg
        # rep -> [0, 42, result]
