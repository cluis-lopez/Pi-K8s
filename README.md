# Raspberry Pi Kubernetes cluster to deploy Spring based apps

This document and the companion scripts serve as a short guide to deploy a Kubernetes (K8s) cluster inside a bunch of Raspberry Pi acting as servers.

The ingredients for the recipe are:

- **3 x Raspberry Pi**: in my case they're two Raspberry Pi 3 with 4 cores, 1GB RAM and one Raspberry Pi 5 with 4 cores and 4GB RAM. The last is confgured as master node while the others are worker nodes. 1GB RAM is poor but you may run 4/5 Spring-Boot based containers on each as every Spring image container takes about 200MB to run
- **1 x Standard x86 Laptop**: running Ubuntu in my case but I guess could be running Windows as long as you may install and run Docker on it

Optional

- **1 x GeeekPi Raspberry Pi Cluster** mini-rack (https://www.amazon.es/dp/B07MW24S61?psc=1&ref=ppx_yo2ov_dt_b_product_details) altough designed for Raspberry Pis 3 & 4 my Raspi5 fits perfectly in the top of the rack. The minirack comes with minifans for each Raspi slot. In my case I'm using the official fan for the model 5 so cannot use (there's no enough space) the mini fan of the rack.
- **1 x Power Supply**: to avoid using individual chargers for each Raspberry I'm using this MANTO 100W Power supply with 4 USB ports (https://www.amazon.es/dp/B0BRKWCBWG?psc=1&ref=ppx_yo2ov_dt_b_product_details). 100W is more than enough for the three Raspis. Each single USB-C port may supply at to 30W which supports even power peaks of the Raspi-5.
- **1 x TP-Link LS105G 5 port 1Gb switch** (https://www.amazon.es/gp/product/B07RPVQY62/ref=ppx_yo_dt_b_asin_title_o00_s01?ie=UTF8&psc=1) to wire each Raspi and avoid using Wifi

## Basic Installation

- Install a fresh Raspbian 64 bit image on every node of your future cluster. To save memory, use the headless (lite) version of the operating system as you won't use GUI on the Raspis and will access them through ssh
- Asign static IP addresses to every node either using reserved IPs on your home DHCP server or manually configuring your /etc/dhcpcd.conf file
- Activate the sshd service using `raspi-config`
- Make all the raspis visible between them, using hostnames through /etc/hosts
- Modify the cmdline.txt file including, at the end of the single line of the file, this entry: `cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory`
_Note: in rapsbian versions <= bullseye, cmdline.txt is under /boot directory. In raspbian version >= bookworn file is under /boot/firmware_
- Reboot all the nodes in your cluster
- Chose one of your raspis as master (control plane) of the kubernetes cluster and install K3s on it using: 
    `curl -sfL http://get.k3s.io | sh -`

- Get the key from the master node and record it somewhere:
    `sudo cat /var/lib/rancher/k3s/server/token`

- Install the worker nodes using the following command on every node
    `curl -sFL http://get.k3s.io | K3S_URL=http://<your_master_node_hostanme_or_ip>:6443 K3S_TOKEN=<your_previously_grabbed_cluster_token> sh -`

- Check the installation using
    `sudo kubectl get nodes`

The command should return a list of cluster nodes like:

```
NAME       STATUS   ROLES                  AGE   VERSION`
raspi5     Ready    control-plane,master   7d    v1.28.6+k3s2
raspi3-2   Ready                           7d    v1.28.6+k3s2
raspi3-1   Ready                           7d    v1.28.6+k3s2
```

Worker nodes are not tagged but you may do so using:
`sudo kubectl label node <nodename> node-role.kubernetes.io/worker=worker`

## Optional: Manage your cluster from your x86 Linux laptop

1- Install kubectl on you linux laptop through 
2- On your raspberry kubernetes master node copy the contents of file `/etc/rancher/k3s/k3s.yaml`
3- On your local PC create a directory `.kube` under you user's home directory
4- Create a file `config` under `.kube/config` and move the contents of the k3s.yaml file from the kubernetes master node
5- Edit that file and modify the entry
    `server: https://127.0.0.1:6443`

to reflect the hostname/ip of your master node like:

    `server: https://master-raspi:6443`

## Optional: create a local repository for container images

The easiest way to create a local repository is running it inside a Docker container.



## Create an Spring container image in a x86 PC/Server that may run in ARM platforms

Assuming your x86 PC has Docker installed already, this example shows how to build an ARM valid image for your Spring application

1- You Dockerfile should use a base image that is available from docker.io compiled for ARM. If your image is java based `FROM openjdk:17.0.1` in your Dockerfile (use the version number you like) is good enough
2- Copy your `target/*.jar` file into the image, expose the needed port and create the container entry point. Your Dockerfile should be as follows:

    ```
    FROM openjdk:17.0.1
    VOLUME /tmp
    COPY target/*.jar app.jar
    EXPOSE 8080
    ENTRYPOINT ["java","-jar","/app.jar"]
    ```

3- Assuming you've created the Dockerfile in the root directory of your maven project execute: `docker buildx build --platform linux/arm64 --load .`

4- A nontagged image should have been created locally:
`# docker image ls`
`<none>                  <none>            83034bdb323d   16 hours ago   547MB`

5- Tagg your newly created image using your repository in the tag name using:
`docker image tag <your repo hostname/ip>:<your repo port>/<tagname>:<version>`

example with the above image using a local repository: 
    `docker image tag 192.168.1.111:5000/clopez/csap-arm:latest 8303`

6- Pull the tagged image on the repository using: 
`docker pull <your repo hostname/ip>:<your repo port>/<tagname>:<version>`

7- Check your repo contains the just uploaded image using:
`curl -X GET <your repo hostname/ip>:<your repo port>/v2/_xcatalog`

You reppository should answer with a json object like: 
`{"repositories":["clopez/csap","clopez/csap-arm"]}`

## Deploy you kubernets deployment and create a service

## Troubleshoot containers in the Raspberrys