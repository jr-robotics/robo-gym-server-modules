# robo-gym-server-modules

Robot Servers and Server Manager software for robo-gym.

For info on how to use this package please visit the [robo-gym website](https://sites.google.com/view/robo-gym) or the main [robo-gym repository](https://github.com/jr-robotics/robo-gym).
# Install

```
pip install robo-gym-server-modules
```

# Server Manager

## How to use

The commands to control the Server Manager are:

- `start-server-manager` starts the Server Manager in the background
- `attach-to-server-manager` attaches the console to the Server Manager tmux session allowing to visualize the status of the Server Manager
- `Ctrl+B, D` detaches the console from the Server Manager tmux session
- `kill-all-robot-servers` kills all the running Robot Servers and the Server Manager
- `kill-server-manager` kills the Server Manager
- `restart-server-manager` kills all the running Robot Servers and the Server Manager and starts the Server Manager in the background

## Testing 

Start the Server Manager and attach to the session with: 

```sh
start-server-manager && attach-to-server-manager
```
Expected output:

```sh
2021-XX-XX XX:XX:XX,XXX - serverManager - INFO - Server Manager started at 50100
```

If you get: `start-server-manager: command not found` it is most probably because your `$PATH` is not set correctly, to fix the problem add:

```bash
export PATH="/home/<your_username>/.local/bin:$PATH"
```

to your `.bashrc` file. 

## Troubleshooting

The Server Manager starts the Robot Server/s in a [tmux](https://github.com/tmux/tmux/wiki) session. To access the session of the Robot Server, first connect to the tmux server with:
```sh
tmux -L ServerManager 
```
Then navigate to the session with `Ctrl+b  )`

[Tmux cheat sheet](https://tmuxcheatsheet.com/)


# Additional info

## How to manually generate python code for the RobotServer

From the repository root folder:
```
 python -m grpc_tools.protoc -Irobo_gym_server_modules/robot_server/grpc_msgs/protos --python_out=robo_gym_server_modules/robot_server/grpc_msgs/python/. --grpc_python_out=robo_gym_server_modules/robot_server/grpc_msgs/python/. robo_gym_server_modules/robot_server/grpc_msgs/protos/robot_server.proto
```

# Acknowledgements 

![euROBIN logo](docs/media/eurobin.png)

Partially developed in the course of the 1st Open Call of [euROBIN](https://www.eurobin-project.eu/).

![Funded by the European Union](docs/media/funded_by_the_eu.png)

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or European Commission. Neither the European Union nor the granting authority can be held responsible for them.

## External contributors

- [Farhang Fadaei](https://github.com/f4rh4ng): Contributed to the development of the initial Panda robot integration.
