### Step 0 - Setup

#### Part 1: Kafka server --> need to setup a kafka server
- Need to create a `docker-compose.yaml` --> you can use chatGPT for that
- Make sure you have the following lines:
      # Broker configurations for single broker setup
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS: 1
      KAFKA_DEFAULT_REPLICATION_FACTOR: 1
      KAFKA_MIN_INSYNC_REPLICAS: 1
- Run in the terminal: `docker compose up -d` => Runs containers in detached mode (in the background).
- run `docker ps` in the terminal to make sure the docker container is up and ready to use

- run in the terminal the following command to make sure the driver is working as expected:
      -  docker logs -f kafka_tutorial-packet-app-1





#### Part 2: Route packets from iphone through PC 
- To enable sniffing packets:
- 1. go to services.msc --> services --> internet connection sharing --> right click --> restart
- 2. Go to settings in your pc --> Network & Internet --> Mobile hotspot --> on (share over WIFI) --> connect to that hotspot through phone
- 3. In iphone: connect to the PC hotspot


#### Part 3 - minikube
1. Open PowerShell as Administrator and run these commands one by one:
- Create a folder for minikube
      - New-Item -Path 'C:\' -Name 'minikube' -ItemType Directory -Force

- Download the executable
      - Invoke-WebRequest -OutFile 'C:\minikube\minikube.exe' -Uri 'https://github.com/kubernetes/minikube/releases/latest/download/minikube-windows-amd64.exe' -UseBasicParsing

- Add it to your System PATH (so you can run 'minikube' from anywhere)
      - $oldPath = [Environment]::GetEnvironmentVariable('Path', [EnvironmentVariableTarget]::Machine)
      if ($oldPath.Split(';') -inotcontains 'C:\minikube'){
      [Environment]::SetEnvironmentVariable('Path', ("$oldPath;C:\minikube"), [EnvironmentVariableTarget]::Machine)
      }
2. start minikube
      - minikube start --driver=docker
3. verify the installation
      - kubectl get nodes

4. Inside your Minikube cluster, the Producer and Consumer pods will look for the Kafka broker using a DNS name. If your service in kafka-local.yaml is named kafka-service, your Python code will connect to kafka-service:9092.

5. Deploy to Minikube
- Once your terminal is refreshed and minikube start has finished, run these commands in order from your KAFKA_TUTORIAL root folder:
      - # 1. Point Docker to Minikube (Important!)
      minikube docker-env | Invoke-Expression

      - # 2. Build your Python app image inside Minikube
      docker build -t kafka-python-app:latest .

      - # 3. Apply the Infrastructure
      kubectl apply -f k8s/config-map.yaml
      kubectl apply -f k8s/kafka-local.yaml

      - # 4. Apply your Apps
      kubectl apply -f k8s/producer-deployment.yaml
      kubectl apply -f k8s/consumer-deployment.yaml

6. Verify the Traffic
      - To see if your Producer is successfully sending messages to the Kafka server, you can check the logs:

      - # Get the name of your producer pod
      - kubectl get pods

      - # View the logs
      - kubectl logs -f <your-producer-pod-name>


#### Part 3: Install oc CLI
1. Download: Go to the OKD/OpenShift Red Hat Downloads page and download the openshift-client-windows.zip (https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/)

2. Extract: Unzip it (you’ll see oc.exe).

3. Add to PATH: * Move oc.exe to a folder like C:\ocp-tool\.

4. Search Windows for "Edit the system environment variables".

5. Click Environment Variables -> Select Path under System Variables -> Edit -> New.

6. Add C:\ocp-tool\ and click OK.

7. Restart PowerShell: Type oc version to confirm it works.

#### Part 4: Red Hat Developer Sandbox (Easiest)
- This is a free, cloud-hosted OpenShift instance provided by Red Hat for 30 days (renewable).

1. Go to the Red Hat Developer Sandbox page: https://sandbox.redhat.com/?intcmp=7013a0000026GZMAA2
2. Log in with a Red Hat account (create one for free).
3. Click "Start using your sandbox."
4. Once it loads, you will see the OpenShift Web Console URL in your browser.
5. Click your name (top right) -> Copy Login Command to get your oc login token for PowerShell.

In your PowerShell window (inside your folder), paste the full command you copied from the browser. It should look like this:
.\oc login --token=sha256~YOUR_SECRET_TOKEN_HERE --server=https://api.your-sandbox-url.com:6443

6. Switch to your project: .\oc get projects --> see the existing projects and replace with your project name:
- .\oc project YOUR_PROJECT_NAME


##### Part 5: use Docker Hub to store our image
- 1. We can create a docker image in Docker Hub:
      - docker build -t roymadpis/kafka-tutorial:latest .
- 2. Tag the image (Linking your local build to your Docker Hub name):
      - docker tag kafka-tutorial:latest roymadpis/kafka-tutorial:latest
- 3. Login to Docker Hub:
      - docker login
- 4. Push the image
      - docker push roymadpis/kafka-tutorial:latest

#### Part 6: Kubernetes - OpenShift
- We have the code (Python), the package (Docker), and the instructions (YAML). OpenShift is the platform that actually hires the "workers" (Servers/Nodes) and ensures they follow our instructions 24/7.

- 2. Update and Apply the ConfigMap. Before starting the scripts, ensure the "Brain" (the config) is correct. Open your k8s/config-map.yaml and make sure it has the exact keys your Python scripts are looking for.
      - Run the command:
      - .\oc apply -f k8s/config-map.yaml
- 3. Deploy the 3 Microservices. Now, "call" the deployments. This will create three "Circles" in your OpenShift Topology view. Run these in order:
      - .\oc apply -f k8s/producer-deployment.yaml
      - .\oc apply -f k8s/driver-deployment.yaml
      - .\oc apply -f k8s/consumer-deployment.yaml
      - .\oc apply -f k8s/kafka-local.yaml

- 4. Verify the Data Flow (The Logs)
      - To see the Driver sorting logs:
            -  .\oc logs -f deployment/packet-driver
      - To see if the Consumer is receiving the transformed data:
            - .\oc logs -f deployment/packet-consumer

./oc.exe get pods -w
#### That's it the setup is ready


### Step 1:
+ Run in the terminal: `producer_sending_packets.py`
- This runs the code that reads the packes from the phone and sends them to the topic configured in the config.yaml file

### Step 2:
+ Run in another terminal: `driver_in_action.py`

This runs the driver code:
- Definnig a driver (consumer + producer)
- The consumer reads the packets in the topic the producer (from step 1) is sending data to
- In the driver_in_action.py file we define a function that determines how to filter/aggregate the incoming packets
- we have a variable (configured also in the config.yaml): `window_size_sec_for_consumer_buffer` that determines how many seconds to wait to get packets

- The producer is taking the output from the filter/aggregation function and sends the data to another topic
- The topic is confifured in the config.yaml file: `topic_name_transformed_packets`

### Step 3:
+ Run in another terminal: `consumer_reading_transformed_packets.py`

- This runs a consumer that reads the transformed packets from the topic: `topic_name_transformed_packets`