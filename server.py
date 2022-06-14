import socket
import select


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(False)
    s.bind(('127.0.0.1', 7788))
    s.listen(128)
    r_list = [s, ]
    while True:
        r1, _, _ = select.select(r_list, [], [])
        for fd in r1:
            if fd == s:
                conn, addr = fd.accept()
                r_list.append(conn)
                print("new client arrive", addr)
            else:
                msg = fd.recv(200)
                if msg:
                    head = int.from_bytes(msg[0:4],byteorder='big')
                    typ = eval(msg[4:])[0]
                    id = eval(msg[4:])[1]
                    content = eval(msg[4:])[2]
                    print("len:%s type:%s id:%s content:%s" % (head, typ, id, content))
                    # print("client %s request:%s" % (addr, msg.decode('gbk')))

                else:
                    print("client %s close" % str(addr))
                    r_list.remove(fd)
                    conn.close()

    s.close()


if __name__ == "__main__":
    main()
