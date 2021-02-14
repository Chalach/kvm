# Software

![](https://i.imgur.com/7KqCuh1.jpg)

## Table of Content
1. [Introduction](#introduction)
1. [Docker and NVIDIA Container Toolkit](#requirements-and-dependencies)
1. [Benchmark](#benchmark)
1. [Kubernetes](#kubernetes)
1. [Terraform](#terraform)
1. [Reference](#reference)

## Introduction
Software and hardware work closely together nowadays and the goal is to automate as much as possible. Using pre-defined configurations and automation tools help in deployment and achieve greater flexibility in data centers. The configuration overhead should be minimized to minimum and most of the decissions are software driven. Software-defined networking (SDN) technology is an approach for network management which creates a dynamic and programmatically efficient network configuration . Microservice architecture is a variant of the service-oriented architecture (SOA) which creates an application as a collection of loosly coupled services. Those are only two of many approaches to manage a infrastructure in a data center. Both are currently state of the art approaches.

The aim is to simulate and recreate such a scenarion by using Docker in combination with Kubernetes and Terraform to provide a infrastructure as a service (IaaS). It should show the capabilities of current data centers. The infrastructure is based on the previously created KVM. A neat feature is the GPU passthrough to provide a container for graphic-intensive tasks as data centers are deploying more and more VMs with GPUs attached to them. 

## Docker
Docker is a container environment which creates, deployes and manages containers. The role of Docker is to create microservices. In order to orchestrate them it is possible to use Docker Swarm but in this case Kubernetes is used as it is more widespread than Docker Swarm.

### Installation
The installation of Docker under Ubuntu 18.04.5 LTS is just using the Docker’s official convenience script. It installs Docker and enables the service for Docker.

```shell=
curl https://get.docker.com | sh && sudo systemctl --now enable docker
```

By default Docker is a root user. It is possible to use Docker as a non-root user by adding the user to the `docker` group.

```shell
sudo usermod -aG docker <your-user>
```

---
**Warning:**

Adding a user to the “docker” group grants them the ability to run containers which can be used to obtain root privileges on the Docker host. Refer to Docker Daemon Attack Surface for more information.

---

### NVIDIA Container Toolkit
The NVIDIA Container Toolkit allows users to build and run GPU accelerated containers. This was the reason why a GPU passthrough was realized with KVM. A Nvidia container will be used check the performance of the GPU passthrough and the focus will afterwards switch to the orchestration without a GPU accelerated container.

#### CUDA (Driver)
To get access to the gragpics card the current driver must be installed. The following commands will install the linux header files for the current kernel, add the CUDA repository to the package manager and install the CUDA driver.

```shell
sudo apt-get install linux-headers-$(uname -r)

distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')

wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-$distribution.pin

sudo mv cuda-$distribution.pin /etc/apt/preferences.d/cuda-repository-pin-600

sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/7fa2af80.pub

echo "deb http://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64 /" | sudo tee /etc/apt/sources.list.d/cuda.list

sudo apt-get update
sudo apt-get -y install cuda-drivers
```

Here are some recommended [post-installation](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions) steps.

#### CUDA Toolkit
The CUDA Toolkit is necessary to use TensorFlow and perform the benchmark on the VM.
```shell
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin

sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600

sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub

sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/ /"

sudo apt-get update

sudo apt-get -y install cuda
```

#### Installation
After the graphic cards driver is installed the Nvidia Container Toolkit can be installed with the following commands.

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
The installation verifies the Docker and Nvidia Container Toolkit installation with the following sample Docker container.

```shell=
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

Important is the `--gpus all` parameter of the above command. It switches all available GPUs into the container.

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


#### Check the CUDA installation on the host system
```shell=
nvcc --version
```

##### Output
```shell=
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2017 NVIDIA Corporation
Built on Fri_Nov__3_21:07:56_CDT_2017
Cuda compilation tools, release 9.1, V9.1.85
```

#### Check the driver version

```shell=
nvidia-smi
```

![](https://i.imgur.com/W160JfL.png)

## Benchmark
The following benchmark will show a quick performance overview of the GPU passthrough differenciated to a previous performed benchmark by myself. The previous benchmark was performed natively on Ubuntu 18.04.5 LTS on the host machine and inside a Nvidia Docker container. Both cases, natively and inside a Nvidia Docker container will be compared in this and the previous benchmark. Mainly the results of the GPU are viewed. The CPU performance from a KVM will not be covered fully in this project.

The first [code](../code/gpu.py) will check if a GPU was found by the Nvidia Container Toolkit. As we already checked those steps previously this is an optional step.

The actuall benchmark [code](../code/matmul.py) supplies the following results compared to the previous performed benchmark by myself.

`tensorflow/tensorflow:latest-gpu` was the used Docker container image for this benchmark. All needed dependencies are pre-installed in this image.

```shell
docker pull tensorflow/tensorflow:latest-gpu
```

### Output
The two tables show the execution time of the same benchmark. Results from table one are from a previous run on a bare-metal Ubuntu 18.04.5 LTS machine and the second results are from the KVM with GPU passthroug of this project.

#### Container (native system)
|    |     CPU    |     GPU    | Speedup |          
|:--:|:----------:|:----------:|:-------:|          
|  1 | 25.2533524 | 1.54997122 |    16   |          
|  2 | 25.7863575 | 1.57203382 |    16   |          
|  3 |  25.487624 | 1.54950751 |    16   |          
|  4 | 25.1899653 | 1.56756516 |    16   |          
|  5 | 25.8140456 | 1.57109671 |    16   |          

#### Container (kernel-based virtual machine)
|    |     CPU    |     GPU    | Speedup |          
|:--:|:----------:|:----------:|:-------:|          
|  1 | 20.3482751 | 1.57650887 |    12   |          
|  2 | 20.3560136 | 1.58154564 |    12   |          
|  3 | 20.5811199 | 1.53468656 |    13   |          
|  4 | 20.5927688 | 1.57579147 |    13   |          
|  5 | 20.4500192 | 1.53758522 |    13   | 

On average the CPU is 20% slower on the KVM Docker machine while the GPU is 0.0005% slower that the native system.

---

##### Disclaimer
The 20% is calculated on the average from the first CPU values (table 1) devided through the average of the second CPU values (table 2).
The 0.0005% is calculated on the average from the first GPI values (table 1) devided through the average of the second GPU values (table 2).

---

##### Diagram
![](https://i.imgur.com/dCDqcG8.png)

##### Discussion
As the diagram shows the performance of the GPU passthrough is bare-metal performance as the CPU has about 20% performance losses.

## Kubernetes
Kubernetes is used to orchestrate containers. Containers respectively microservices can be scaled up and down by Kubernetes.

```shell
sudo apt-get update && sudo apt-get install -y apt-transport-https gnupg2 curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
```

### Use case
Creation of a K8 cluster with auto-scaling, load-balancing, self-healing.

## Terraform
Terraform is an open-source infrastructure as code software tool. Infrastructure as a Service (IaaS) is an ever-growing sector that is located in the cloud area. Many customer do not like to manage their hardware locally at their facillity and move their infrastructure into the cloud. This saves space, resources, money and personell at a given fee. The infrastructure is managed externally with higher performance at a lower price. Terraform helps to manage such a infrastructure.

### Installation
The following commands will install Terraform on Ubuntu 18.04.5 LTS.

```shell
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
```

```shell
sudo apt-add-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
```

```shell
sudo apt install terraform
```

### Use case
New deployment of virtual machines.

## Reference
* https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

* https://medium.com/onfido-tech/container-orchestration-with-kubernetes-an-overview-da1d39ff2f91

* https://www.terraform.io/

* https://www.linuxfoundation.org/