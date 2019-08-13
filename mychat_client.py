import socket
import threading
import os

lock = threading.Lock()
#客户端


class MyChatClient:
    def __init__(self):
        self.__socket = self.init_socket()
        self.__server_addr = ("192.168.53.9",4080)
        self.__username = "张三丰"
        self.__alert = "请选择您的操作：\n(0)下线退出\n(1)打印在线用户列表\n(回车+to:对方用户名：内容)和在线用户聊天"

    @staticmethod
    def init_socket():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return s

    def start(self):
        ret = self.login()
        if not ret:
            return

        # 开启子线程，接受数据
        thread = threading.Thread(target=MyChatClient.recv_data,args=(self,))
        thread.start()

        print(self.__alert)
        while True:
            s = input()
            if s == "0":
                self.logout()
                return       #结束进程

            elif s == "1":
                self.request_user_list()
            elif s == "":
                #聊天
                with lock:
                    s = input()
                if s.startswith("to:") or s.startswith("to："):
                    self.send_massage(s)
                else:
                    print("输入错误")
            else:
                print("输入错误")

    #登录
    def login(self):
        content = "<[LOGIN]>|{}".format(self.__username)
        self.__socket.sendto(content.encode("utf-8"),self.__server_addr)

        #接受回执
        data, addr = self.__socket.recvfrom(1024)
        data = data.decode("utf-8")
        if data == "<[LOGIN_SUCCESS]>":
            print("登录成功，您已上线!")
            return True
        else:
            print("登录失败，您的用户名或有重复，请跟换后使用")
            return False

    #下线
    def logout(self):
        content = "<[LOGOUT]>|{}".format(self.__username)
        self.__socket.sendto(content.encode("utf-8"), self.__server_addr)
        print("感谢你的使用，再见！")

    # 请求打印列表
    def request_user_list(self):
        content = "<[SHOW_USR_LIST]>|{}".format(self.__username)
        self.__socket.sendto(content.encode("utf-8"), self.__server_addr)

    # 发送聊天信息
    def send_massage(self,message):
        #"to:xxx:hello"
        # 中文冒号，转英文冒号
        message = ":".join(message.split("："))
        ls = message.split(":")
        # <[SEND_MESSAGE]>|fromusername|tousername|words
        content = "<[SEND_MESSAGE]>|{}|{}|{}".format(self.__username, ls[1], ls[-1])
        self.__socket.sendto(content.encode("utf-8"), self.__server_addr)

    # 开一个子线程，接受数据
    def recv_data(self):
        while True:
            # 判断接受到的数据，任务分发
            data, addr = self.__socket.recvfrom(1024)
            data = data.decode("utf-8")
            ctl = data.split("|")[0]
            if ctl == "<[LOGOUT_SUCCESS]>":
                break
            ctl_dict = {
                "<[USR_LIST]>": MyChatClient.show_user_list,
                "<[SEND_MESSAGE]>": MyChatClient.show_recv_message,
            }
            with lock:
                ctl_dict[ctl](self, data)
                print(self.__alert)


    def show_user_list(self,data):
        print("=======================")
        for i in data.split("|")[1:]:
            print(i)
        print("=======================")

    def show_recv_message(self,data):
        ls = data.split("|")
        s = "from:{}:\n  {}".format(ls[1],ls[-1])
        print(s)






c = MyChatClient()
c.start()


