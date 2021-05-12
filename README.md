# robo-gym-server-modules

Robot Servers and Server Manager software for robo-gym.

For info on how to use this package please visit the [robo-gym website](https://sites.google.com/view/robo-gym) or the main [robo-gym repository](https://github.com/jr-robotics/robo-gym).
## Install

```
pip install robo-gym-server-modules
```

## Server Manager

### How to use

The commands to control the Server Manager are:

- `start-server-manager` starts the Server Manager in the background
- `attach-to-server-manager` attaches the console to the Server Manager tmux session allowing to visualize the status of the Server Manager
- `Ctrl+B, D` detaches the console from the Server Manager tmux session
- `kill-all-robot-servers` kills all the running Robot Servers and the Server Manager
- `kill-server-manager` kills the Server Manager
- `restart-server-manager` kills all the running Robot Servers and the Server Manager and starts the Server Manager in the background

## Additional info

### How to manually generate python code for the RobotServer

From the repository root folder:
```
 python -m grpc_tools.protoc -Irobo_gym_server_modules/robot_server/grpc_msgs/protos --python_out=robo_gym_server_modules/robot_server/grpc_msgs/python/. --grpc_python_out=robo_gym_server_modules/robot_server/grpc_msgs/python/. robo_gym_server_modules/robot_server/grpc_msgs/protos/robot_server.proto
```