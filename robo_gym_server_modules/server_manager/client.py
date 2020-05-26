
import grpc
from grpc import RpcError
from robo_gym_server_modules.server_manager.grpc_msgs.python3 import server_manager_pb2, server_manager_pb2_grpc



class Client():

    def __init__(self, ip, lower_bound_port = 50100, upper_bound_port= 50200):

        assert self._connect_to_rl_srv_mng(ip,lower_bound_port,upper_bound_port)

    def start_new_server(self, cmd, gui):

        i =0
        while (i<1000):
            try:
                print('Starting new Robot Server | Tentative {}'.format(str(i+1)))
                rl_server = self.stub.StartNewServer(request= server_manager_pb2.RobotServer(cmd= cmd, \
                                                                                             gui= gui), timeout =240)

                if rl_server.success:
                    print('Successfully started Robot Server at {}:{}'.format(self.ip,str(rl_server.port)))
                    return (self.ip + ':'+str(rl_server.port))
                else:
                    pass
            except:
                pass
            i+=1

        raise RuntimeError("Failed multiple tentatives to start new Robot Server")

    def kill_server(self, port):

        # Extract port
        if isinstance(port, int):
            pass
        elif isinstance(port, str):
            try:
                address = port.split(':')
                port=int(address[1])
            except:
                raise RuntimeError("port argument is malformed")
        else:
            raise RuntimeError("port argument is malformed")

        i=0
        while (i<1000):
            try:
                print('Killing Robot Server at {}:{} | Tentative {}'.format(self.ip,str(port),str(i+1)))
                result = self.stub.KillServer(request= server_manager_pb2.RobotServer(port=port), timeout =60)

                if result.success:
                    print('Successfully killed Robot Server at {}:{}'.format(self.ip,str(port)))
                    return True
                else:
                    pass
            except:
                pass
            i+=1

        raise RuntimeError("Failed 5 tentatives of killing Robot Server")

    def kill_all(self):

        msg = server_manager_pb2.RobotServer()
        return self.stub.KillAllServers(msg).success

    def _connect_to_rl_srv_mng(self,ip,lower_bound_port,upper_bound_port):

        for port in range(lower_bound_port,upper_bound_port):
            try:
                self.channel = grpc.insecure_channel((ip + ':' + str(port)))
                self.stub = server_manager_pb2_grpc.ServerManagerStub(self.channel)
                self.ip = ip
                self._verify_connection()
                return True
            except RpcError as rpc_error:
                pass
        raise RuntimeError("Failed to connect to Server Manager")

    def _verify_connection(self):

        return self.stub.VerifyConnection(server_manager_pb2.Empty(), timeout=20).alive
