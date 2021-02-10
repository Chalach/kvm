### Software
Installing `Docker` and `Nvidia Docker Contianer` to perform a benchmark.

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

#### Setting up Docker

```shell=
curl https://get.docker.com | sh && sudo systemctl --now enable docker
```

#### Setting up NVIDIA Container Toolkit

```shell=
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
&& curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```


##### Install the nvidia-docker2 package (and dependencies)

```shell=
sudo apt update
sudo apt install nvidia-docker2
```

It is neccessary to restart the Docker daemon that the changes take affect

```shell=
sudo systemctl restart docker
```

#### Verify the installation
The installation can be verified with the following sample Docker container.
```shell=
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

##### Output

```
Wed Feb 10 19:37:29 2021       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 460.32.03    Driver Version: 460.32.03    CUDA Version: 11.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  GeForce GTX 970     Off  | 00000000:09:00.0  On |                  N/A |
|  0%   38C    P5    26W / 163W |    334MiB /  4040MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
+-----------------------------------------------------------------------------+
```

##### (Optional) Add user to the Docker group
The user can be added to the Docker group.

:::danger
The docker group grants privileges equivalent to the root user. For details on how this impacts security in your system, see Docker Daemon Attack Surface.
:::

```shell=
sudo usermod -aG docker $USER
```

### Use Nvidia GPU on the host system
In order to fully use the GPU on the host system it is neccessary to install the needed drivers.
#### Install CUDA
```shell=
sudo apt install nvidia-cuda-toolkit
```


#### Check Version
```shell=
nvcc --version
```

#### Output
```shell=
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2017 NVIDIA Corporation
Built on Fri_Nov__3_21:07:56_CDT_2017
Cuda compilation tools, release 9.1, V9.1.85
```

Check if the Driver loaded successfully.

```shell=
nvidia-smi
```

![](https://i.imgur.com/W160JfL.png)