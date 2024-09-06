from typing import Any
import threading
import grpc
from grpc import RpcError
from robo_gym_server_modules.server_manager.grpc_msgs.python3 import server_manager_pb2, server_manager_pb2_grpc


class Client():

    def __init__(self, ip, lower_bound_port=50100, upper_bound_port=50200):

        assert self._connect_to_rl_srv_mng(ip, lower_bound_port, upper_bound_port)

    def start_new_server(self, cmd, gui):

        i = 0
        max_tentatives = 10
        while (i < max_tentatives):
            try:
                print('Starting new Robot Server | Tentative {} of {}'.format(str(i + 1), str(max_tentatives)))
                rl_server = self.stub.StartNewServer(request=server_manager_pb2.RobotServer(cmd=cmd, \
                                                                                            gui=gui), timeout=240)

                if rl_server.success:
                    print('Successfully started Robot Server at {}:{}'.format(self.ip, str(rl_server.port)))
                    return ('{}:{}'.format(self.ip, str(rl_server.port)))
                else:
                    pass
            except:
                pass
            i += 1

        raise RuntimeError('Failed {} tentatives to start new Robot Server'.format(str(max_tentatives)))

    def kill_server(self, port):
        port = Client.extract_port(port)

        i = 0
        max_tentatives = 10
        while (i < max_tentatives):
            try:
                print('Killing Robot Server at {}:{} | Tentative {} of {}'.format(self.ip, str(port), str(i + 1),
                                                                                  str(max_tentatives)))
                result = self.stub.KillServer(request=server_manager_pb2.RobotServer(port=port), timeout=60)

                if result.success:
                    print('Successfully killed Robot Server at {}:{}'.format(self.ip, str(port)))
                    return True
                else:
                    pass
            except:
                pass
            i += 1

        raise RuntimeError('Failed {} tentatives of killing Robot Server'.format(str(max_tentatives)))

    def kill_server_async(self, port):
        port = Client.extract_port(port)
        stub = self.stub
        killer_thread = threading.Thread(target=kill_server_static, args=[stub, port])
        killer_thread.start()

    @staticmethod
    def extract_port(port: Any) -> int:
        # Extract port
        if isinstance(port, int):
            pass
        elif isinstance(port, str):
            try:
                address = port.split(':')
                port = int(address[1])
            except:
                raise RuntimeError('port argument is malformed')
        else:
            raise RuntimeError('port argument is malformed')
        return port



    def kill_all(self):

        msg = server_manager_pb2.RobotServer()
        return self.stub.KillAllServers(msg).success

    def _connect_to_rl_srv_mng(self, ip, lower_bound_port, upper_bound_port):

        for port in range(lower_bound_port, upper_bound_port):
            try:
                self.channel = grpc.insecure_channel('{}:{}'.format(ip, str(port)))
                self.stub = server_manager_pb2_grpc.ServerManagerStub(self.channel)
                self.ip = ip
                self._verify_connection()
                return True
            except RpcError as rpc_error:
                pass
        raise RuntimeError('Failed to connect to Server Manager')

    def _verify_connection(self):

        return self.stub.VerifyConnection(server_manager_pb2.Empty(), timeout=20).alive

def kill_server_static(stub: server_manager_pb2_grpc.ServerManagerStub, port: int):
    try:
        print('Attempting to kill Robot Server at port {} in static context'.format(port))
        stub.KillServer(request=server_manager_pb2.RobotServer(port=port), timeout=60)
        print('Successfully killed Robot Server at port {} in static context'.format(port))
    except:
        print('Failed to kill Robot Server at port {} in static context'.format(port))
