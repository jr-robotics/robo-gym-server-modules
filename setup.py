import setuptools
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'robo_gym_server_modules'))
from version import VERSION

if sys.version_info.major == 2:
    libtmux = 'libtmux==0.8.5'
else:
    libtmux = 'libtmux'

setuptools.setup(
    name='robo-gym-server-modules',
    version=VERSION,
    description='Robot Servers and Server Manager code for robo-gym',
    url='https://github.com/jr-robotics/robo-gym-server-modules',
    author="Matteo Lucchi, Friedemann Zindler, Bernhard Reiterer, Benjamin Breiling",
    author_email="bernhard.reiterer@joanneum.at",
    packages=setuptools.find_packages(),
    include_package_data=True,
    # data_files=[('robo_gym_server_modules', ['logging_config.yml'])],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
    'grpcio',
    "protobuf >= 3.20, < 3.21",
    libtmux,
    'pyyaml'
    ],
    python_requires='>=3.8',
    scripts = [ 'bin/attach-to-server-manager',
                'bin/kill-all-robot-servers',
                'bin/kill-server-manager',
                'bin/start-server-manager',
                'bin/restart-server-manager'],
)
