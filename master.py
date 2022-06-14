import heapq
import multiprocessing
import socket
import select

import worker



class Master(object):

    def __init__(self, address, cpu_num) -> None:
        self.sock = self.create_sock(address)
        self.workers_num = cpu_num
        self.last_worker = 0
        self.workers_port = []
        self.master_to_worker = []
        self.workers = self.create_workers(self.workers_num)

    @staticmethod
    def create_sock(address):
        """ 创建 master socket
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(address)
        sock.listen(10000)
        return sock
    
    def create_workers(self, num):
        """ 创建workers 
        """
        port = 9899
        workers = []
        for i in range(num):
            self.workers_port.append(port)
            w = worker.Worker(self.sock, i, ("127.0.0.1", port))
            workers.append(w.make_worker())
            port += 1
        return workers

    def start(self):
        """ 首先开启worker 初始化和workers的通信， 然后开启masterr进程
        """
        i = 0
        for w in self.workers:
            w.start()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", self.workers_port[i]))
            self.master_to_worker.append(sock)
            i += 1
        listen_fd = [self.sock] + self.master_to_worker

        print("INFO: start server")

        queue = []

        while True:
            try:
                r, _, _ = select.select(listen_fd, [], [], 9999)
                for fd in r:
                    if fd != self.sock:
                        res = fd.recv(5)
                        i = listen_fd.index(fd)
                        # 尝试负载均衡，挑选 压力小的worker
                        heapq.heappush(queue, (int(res.decode()), i))
                    else:
                        if queue:
                            n, fd = heapq.heappop(queue)
                            print(n, fd)
                            listen_fd[fd].send(b'1')
            except Exception as e:
                self.sock.close()
                print("end !")

if __name__ == "__main__":
    p = multiprocessing.cpu_count()
    print(p)
    master = Master(('127.0.0.1', 9898), p-1)
    master.start()
