# robo-gym-server-modules

Robot Servers and Server Manager software for robo-gym.

For info on how to use this package please visit the [robo-gym website](https://sites.google.com/view/robo-gym) or the main [robo-gym repository](https://github.com/jr-robotics/robo-gym).
## Install

```
pip install robo-gym-server-modules
```

## Server Manager

### How to use

`start-server-manager` : Start the Server Manager in the background

`attach-to-server-manager` : Attach to Server Manager sessions to see its status

`kill-server-manager` : Kill the Server Manager

`kill-all-robot-servers` : Kill all the existing Robot Servers

## Additional info

### How to manually generate python code for the RobotServer

From the repository root folder:
```
 python -m grpc_tools.protoc -Irobo_gym_server_modules/robot_server/grpc_msgs/protos --python_out=robo_gym_server_modules/robot_server/grpc_msgs/python/. --grpc_python_out=robo_gym_server_modules/robot_server/grpc_msgs/python/. robo_gym_server_modules/robot_server/grpc_msgs/protos/robot_server.proto
```