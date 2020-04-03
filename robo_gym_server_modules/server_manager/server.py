#!/usr/bin/env python3

import grpc
import libtmux
import itertools
import time
import socket
from contextlib import closing
from concurrent import futures

from robo_gym_server_modules.robot_server.client import Client
from robo_gym_server_modules.server_manager.grpc_msgs.python3 import server_manager_pb2, server_manager_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def find_free_port(lower_bound=0,upper_bound=1):
    # If no lower_bound and upper_bound are passed it uses a random port
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        for i in range(lower_bound,upper_bound):
            try:
                s.bind(('localhost', i))
                return s.getsockname()[1]
            except socket.error as e:
                pass


class ServerManager():
    def __init__(self,):

        self.tmux_srv = libtmux.Server(socket_name = 'ServerManager')
        self.new_session_ID = itertools.count()
        self.kill_server()

    def new_session(self, name = None):

        return self.tmux_srv.new_session(session_name = name, kill_session = True, attach = False)

    def kill_session(self, session_name):

        if self.tmux_srv.has_session(session_name):
            session = self.tmux_srv.find_where({"session_name":session_name})
            if session is None:
                return False
            window = session.select_window("grpc_server")
            pane = window.attached_pane
            # Send Ctrl-C to kill all processes properly
            pane.send_keys(cmd = ("C-c"), suppress_history = False)
            # Wait some time to allow to kill processes
            time.sleep(15)
            # Kill tmux session
            self.tmux_srv.kill_session(session_name)
            return True
        else:
            return False

    def list_sessions(self):

        print (self.tmux_srv.list_sessions())

    def kill_server(self):

        self.tmux_srv.kill_server()

    def add_rl_server(self, cmd, gui ):

        grpc_port = find_free_port()

        session = self.new_session(name = repr(grpc_port))
        server_w = session.new_window(window_name = "grpc_server")
        server_pane = server_w.attached_pane

        ros_port = find_free_port()
        server_pane.send_keys(cmd = ("export ROS_MASTER_URI=http://localhost:"+repr(ros_port)), suppress_history = False)

        gazebo_port = find_free_port()
        server_pane.send_keys(cmd = ("export GAZEBO_MASTER_URI=http://localhost:"+repr(gazebo_port)), suppress_history = False)

        if gui:
            server_pane.send_keys(cmd = ("export DISPLAY=:0"), suppress_history = False)

        # Launch simulation
        server_pane.send_keys(cmd="{} gui:={} server_port:={}".format(cmd, ("true" if gui else "false"),repr(grpc_port)) ,suppress_history = False)

        time.sleep(10)
        for i in range(10):
            time.sleep(5)
            try:
                test_client= Client('localhost:'+repr(grpc_port))
                assert (len(test_client.get_state())> 1)
                return (grpc_port)
            except grpc.RpcError as rpc_error:
                pass
            except AssertionError as a_error:
                pass
        return('Could not start rl_bridge_server')



class ServerManagerServicer(server_manager_pb2_grpc.ServerManagerServicer):
    def __init__(self):
        self.srv_mngr = ServerManager()

    def __del__(self):
        self.srv_mngr.kill_server()
        print("tmux server killed")

    def StartNewServer(self, request, context):

        try:
            rl_msg = server_manager_pb2.RobotServer()
            rl_server = self.srv_mngr.add_rl_server(cmd= request.cmd, gui= request.gui)
            assert isinstance(rl_server, int)
            rl_msg.port = rl_server
            rl_msg.success = 1
            print ("Robot Server started at {} successfully".format(repr(rl_server)))
            return rl_msg

        except:
            print("Failed to add Robot Server")
            return server_manager_pb2.RobotServer(success=0)

    def KillServer(self, request, context):
        try:
            assert request.port
            assert self.srv_mngr.kill_session(repr(request.port))
            print ("Robot Server " + repr(request.port) + " killed")
            return server_manager_pb2.RobotServer(success=1)

        except:
            print ("Failed to kill Robot Server " + repr(request.port))
            return server_manager_pb2.RobotServer(success=0)

    def KillAllServers(self, request, context):

        try:
            self.srv_mngr.kill_server()
            self.srv_mngr = ServerManager()
            print ("All servers killed")
            return server_manager_pb2.RobotServer(success=1)
        except:
            return server_manager_pb2.RobotServer(success=0)

    def VerifyConnection(self, request, context):
        return server_manager_pb2.Status(alive=1)





def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_manager_pb2_grpc.add_ServerManagerServicer_to_server(
        ServerManagerServicer(),server)
    port = find_free_port(50100,50200)
    server.add_insecure_port('[::]:'+repr(port))
    server.start()
    print("Server Manager started at " +repr(port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)






if __name__== "__main__":
    try:
        serve()
    except (KeyboardInterrupt, SystemExit):
        pass
