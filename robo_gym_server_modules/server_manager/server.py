#!/usr/bin/env python3

import grpc
import libtmux
import itertools
import time
import socket
from contextlib import closing
from concurrent import futures
import logging, logging.config
import yaml
import os

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
            session = self.tmux_srv.find_where({'session_name':session_name})
            if session is None:
                return False
            window = session.select_window('grpc_server')
            pane = window.attached_pane
            # Send Ctrl-C to kill all processes properly
            pane.send_keys(cmd = ('C-c'), suppress_history = False)
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
        server_w = session.new_window(window_name = 'grpc_server')
        server_pane = server_w.attached_pane

        ros_port = find_free_port()
        server_pane.send_keys(cmd= 'export ROS_MASTER_URI=http://localhost:{}'.format(repr(ros_port)), suppress_history = False)

        gazebo_port = find_free_port()
        server_pane.send_keys(cmd= 'export GAZEBO_MASTER_URI=http://localhost:{}'.format(repr(gazebo_port)), suppress_history = False)

        # Launch simulation
        server_pane.send_keys(cmd= '{} gui:={} server_port:={}'.format(cmd, ('true' if gui else 'false'),repr(grpc_port)) ,suppress_history = False)

        time.sleep(10)
        logger.info('Trying to get state from Robot Server...')
        max_tentatives = 20
        for i in range(max_tentatives):
            try:
                logger.info('Tentative {} of {}'.format(str(i),max_tentatives))
                test_client= Client('localhost:{}'.format(repr(grpc_port)))
                assert (len(test_client.get_state_msg().state_dict.keys()) >= 1)
                return (grpc_port)
            except grpc.RpcError:
                logger.debug('Failed to get state from Robot Server', exc_info=True)
                pass
            except AssertionError:
                logger.debug('Length of Robot Serve state received is not > 1', exc_info=True)
                pass
            logger.info('Waiting 5s before next tentative ...')
            time.sleep(5)
        logger.error('Could not start Robot Server', exc_info= True)
        return None



class ServerManagerServicer(server_manager_pb2_grpc.ServerManagerServicer):
    def __init__(self):
        self.srv_mngr = ServerManager()

    def __del__(self):
        self.srv_mngr.kill_server()
        logger.info('tmux server killed')

    def StartNewServer(self, request, context):
        logger.info('Starting Robot Server...')
        try:
            rl_msg = server_manager_pb2.RobotServer()
            rl_server = self.srv_mngr.add_rl_server(cmd= request.cmd, gui= request.gui)
            assert isinstance(rl_server, int)
            rl_msg.port = rl_server
            rl_msg.success = 1
            logger.info('Robot Server started at %s successfully', repr(rl_server))
            return rl_msg

        except:
            logger.error('Failed to add Robot Server', exc_info=True)
            return server_manager_pb2.RobotServer(success=0)

    def KillServer(self, request, context):
        try:
            assert request.port
            assert self.srv_mngr.kill_session(repr(request.port))
            logger.info('Robot Server {} killed'.format(repr(request.port)))
            return server_manager_pb2.RobotServer(success=1)

        except:
            logger.error('Failed to add Robot Server {}'.format(repr(request.port)), exc_info=True)
            return server_manager_pb2.RobotServer(success=0)

    def KillAllServers(self, request, context):

        try:
            self.srv_mngr.kill_server()
            self.srv_mngr = ServerManager()
            logger.info('All servers killed')
            return server_manager_pb2.RobotServer(success=1)
        except:
            return server_manager_pb2.RobotServer(success=0)

    def VerifyConnection(self, request, context):
        return server_manager_pb2.Status(alive=1)





def serve():
    initialize_logger()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_manager_pb2_grpc.add_ServerManagerServicer_to_server(
        ServerManagerServicer(),server)
    port = find_free_port(50100,50200)
    server.add_insecure_port('[::]:{}'.format(repr(port)))
    server.start()
    logger.info('Server Manager started at {}'.format(repr(port)))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

def initialize_logger():
    global logger 
    
    package_path = os.path.join(os.path.dirname(__file__), '..')
    with open(os.path.join(package_path, 'logging_config.yml'), 'r') as stream:
        config = yaml.safe_load(stream)
    config['handlers']['file']['filename'] = os.path.join(package_path, config['handlers']['file']['filename'] )
    logging.config.dictConfig(config)
    logger = logging.getLogger('serverManager')

if __name__== '__main__':
    try:
        serve()
    except (KeyboardInterrupt, SystemExit):
        pass
