import grpc
from robo_gym_server_modules.robot_server.grpc_msgs.python import robot_server_pb2, robot_server_pb2_grpc

class Client():

    def __init__(self, ip):

        self.channel = grpc.insecure_channel(ip)
        self.robot_server_stub = robot_server_pb2_grpc.RobotServerStub(self.channel)

    def set_state(self, state):
        msg = self.robot_server_stub.SetState(robot_server_pb2.State(state = state), timeout = 60)
        return msg.success

    def get_state(self,):
        msg = self.robot_server_stub.GetState(robot_server_pb2.State(), timeout = 20)
        if msg.success == 1:
            return msg.state
        else:
            raise Exception('Error while retrieving state')

    def send_action(self, action):
        msg = self.robot_server_stub.SendAction(robot_server_pb2.Action(action = action), timeout = 20 )
        return msg.success
