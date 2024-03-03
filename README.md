# Raspberry Pi Kubernetes cluster to deploy Spring based apps

## Basic Installation

1- Install a fresh Raspbian 64 bit image on every node of your future cluster
2- Asign static IP addresses to every node either using reserved IPs on your home DHCP server or manually configuring your /etc/dhcpcd.conf file
3- Make all the raspis are visible between them, using hostnames through /etc/hosts
4- Modify the cmdline.txt file including, at the end of the single line of the file, this entry: "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory"
Note: in rapsbian versions <= bullseye, cmdline.txt is under /boot directory. In raspbian version >= bookworn file is under /boot/firmware
5- Reboot all the nodes in your cluster
6- Chose one of your raspis as master (control plane) of the kubernetes cluster and install K3s on it using: 
    `curl -sfL http://get.k3s.io | sh -`

7- Get the key from the master node and record it somewhere:
    `sudo cat /var/lib/rancher/k3s/server/token`

8- Install the worker nodes using the following command on every node
    `curl -sFL http://get.k3s.io | K3S_URL=http://<your_master_node_hostanme_or_ip>:6443 K3S_TOKEN=<your_previously_grabbed_cluster_token> sh -`

9- Check the installation using
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

## Optional: create a local container images repository

# Create an Spring container image in a x86 PC/Server that may run in ARM platforms

1- Assuming your x86 PC has Docker installed already, the example shows how to build an ARM valid image for your Spring application
2- You Dockerfile should use a base image that is available from docker.io compiled for ARM. If your image is java based `FROM openjdk:17.0.1` in your Dockerfile (use the version number you like) is good enough
3- Copy your `target/*.jar` file into the image, expose the needed port and create the container entry point. Your Dockerfile should be as follows:

    ```
    FROM openjdk:17.0.1
    VOLUME /tmp
    COPY target/*.jar app.jar
    EXPOSE 8080
    ENTRYPOINT ["java","-jar","/app.jar"]
    ```

4- Assuming you've created the Dockerfile in the root directory of your maven project execute: `docker buildx build --platform linux/arm64 --load .`

5- A nontagged image should have been created locally:
`# docker image ls`
`<none>                  <none>            83034bdb323d   16 hours ago   547MB`

6- Tagg your newly created image using your repository in the tag name using:
`docker image tag <your repo hostname/ip>:<your repo port>/<tagname>:<version>`

example with the above image using a local repository: 
    `docker image tag 192.168.1.111:5000/clopez/csap-arm:latest 8303`

7- Pull the tagged image on the repository using: 
`docker pull <your repo hostname/ip>:<your repo port>/<tagname>:<version>`

8- Check your repo contains the just uploaded image using:
`curl -X GET <your repo hostname/ip>:<your repo port>/v2/_xcatalog`

You reppository should answer with a json object like: 
`{"repositories":["clopez/csap","clopez/csap-arm"]}`

## Deploy you kubernets deployment and create a service

## Troubleshoot containers in the Raspberrys