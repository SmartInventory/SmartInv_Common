# Common SmartInventory

Common package for python soft of SmartInventory

# How to build 

`python3 -m pip install --upgrade build`
`python3 -m build`

# Deployment 

## How to deploy in production

### Create the kubernetes cluster

On your computer start a webserver that serve files in `./infra/cloud-init/`

Example :
``
infra/cloud-init/ $ docker run --rm -p "8002:80" -v $(pwd):/usr/share/nginx/html nginx
``

Make sure you can access the server by connecting from another computer `http://{{comupter_ip}}:8002/smartinv-master.yml`

Download the [k3os](https://github.com/rancher/k3os/releases/download/v0.21.5-k3s2r1/k3os-amd64.iso) ISO 

#### CloudInit configuration

In all the file change the `ssh_authorized_keys` part with your ssh key.
In the master file change the `token` section with another random string

[Full documentation](https://github.com/rancher/k3os#configuration-reference)

#### Master Node

Recommended spec : 4Go RAM : 10Go Disk

* Boot on the ISO and select "Install"
* When asked to use `cloud-init` say yes and enter the url to the master file (careful, it's in QWERTY).
* The server will configure itself from here. 
* When finished, login using ssh username `rancher` and your ssh key.
* Recover the IP address of the master node and change the IP in node01 and node02 cloudinit file with the master ip (section `server_url`)
* Recover the cluster key : `sudo cat /var/lib/rancher/k3s/server/node-token`
  * Put this key in the `token` section of the node01 and node02 cloudinit files


#### Worker nodes

Recommended spec : 2Go RAM : 10Go Disk

* Create node01 and node02 
* Boot on the ISO and select "Install"
* When asked to use `cloud-init` say yes and enter the url to the node file (careful, it's in QWERTY).
* Tag the nodes as workers `kubectl label node {{node_id}} node-role.kubernetes.io/worker=worker`
* The nodes are configured


#### Access the cluster

* On your machine, get `kubectl` 
* On the master host get the credentials : `kubectl get config --raw` and copy it in `~/.kube/config/`
* Change the Ip  with the master IP
* Test by recovering all the services : `kubectl get svc`


#### Create the dashboard service

* Go to `infra/k8s/users`
* Create users roles : `kubectl apply -f dashboard-user.yml`
* Create dashboard service : ` kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.5.0/aio/deploy/recommended.yaml`
* Proxy the connection `kubectl proxy -p 8006 &`
* Generate a token : `kubectl -n kubernetes-dashboard create token admin-user`
* Access the dashboard : [http://localhost:8006/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login](http://localhost:8006/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login)

#### Create the nfs storage class

* Go to `infra/k8s/storage` 
* In `patch_nfs_details.yml` change `NFS_SERVER` and `NFS_PATH` to match your config 
  * Caution : On synology nas, disable the Mapping
* Apply : `kubectl apply -f .`

#### Create the docker registry

* `kubectl apply -f docker-registry.yml`

#### Create namespaces

* `kubectl apply -f infra/k8s/analytic/namespace.yml -f infra/k8s/smartinv/namespace.yml`

#### Create the secrets

* Go to `infra/k8s/secrets`
* Apply : `kubectl apply -f .`
* Configure the secrets in the dashboard (select the right namespace)
* For the rabbitmq file : send a definition that you have already created or configure it yourself after deployment
  * `http://{{master_node}}:15672`
  * user : `guest` password : `guest`
* For the `inv-config` and `bo-config` 
  * Copy the `configuration_sample.ini` for the project and fill it with the information you previously filled 
  * The hostnames are the name of the deployment (`backoffice-psql`/`inventory-psql`/`couchdb`/`rabbitmq`...)

#### Create configmap 

* `kubectl apply -f infra/k8s/configmap`

#### Build smartinv images

* On your computer in the project directory
  * Backoffice Backend :
    * `docker build . -t {{masternode_ip}}:5000/smartinventory_backoffice:stable`
    * `docker push {{masternode_ip}}:5000/smartinventory_backoffice:stable`
  * Backoffice Frontend :
    * `docker build . -t {{masternode_ip}}:5000/smartinv_bo_front:stable`
    * `docker push {{masternode_ip}}:5000/smartinv_bo_front:stable`
  * Inventory Backend :
    * `docker build . -t {{masternode_ip}}:5000/smartinventory_inventory:stable`
    * `docker push {{masternode_ip}}:5000/smartinventory_inventory:stable`
  * Inventory Frontend :
    * `docker build . -t {{masternode_ip}}:5000/smartinv_bo_front:stable`
    * `docker push {{masternode_ip}}:5000/smartinv_bo_front:stable`


#### Deploy smartinventory

* In `infra/k8s/smartinv`
* Deploy redis :
  * `kubectl apply -f redis/.`
* Deploy databases :
  * `kubectl apply -f databases/.`
* Deploy couchDB :
  * `kubectl apply -f couchdb.yml`
* Deploy Rabbitmq :
  * `kubectl apply -f rabbitmq.yml`
* Deploy Vue :
  * `kubectl apply -f vue/.`
* Deploy Python :
  * `kubectl apply -f python/.`
* Deploy Ingress :
  * `kubectl apply -f ingress/.`

The app is accessible on `(bo|in).smartinv.local`. Make sure that these FQDN redirect to the master node ip.

The application should work. Bravo!

#### Create the first user 

* Get the pod name : `kubectl get pod --namespace=smartinventory`
  * `bo-back-{{ID}}`
* `kubectl exec -it bo-back-{{ID}} --namespace=smartinventory -- /bin/sh`
* `/app # python manage.py createsuperuser`
* Fill up the email and password for the first user


You can now connect to `bo.smartinv.local` with the id you just created. Congrats!