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

### Step 3:
+ Run in another terminal: `consumer_reading_transformed_packets.py`

- This runs a consumer that reads the transformed packets from the topic: `topic_name_transformed_packets`



#### Jenkins:
1. Since we have docker installed we can start a Jenkins server with a single command. Open the terminal and run:
      - docker run -d `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v //var/run/docker.sock:/var/run/docker.sock `
  --name jenkins-server `
  jenkins/jenkins:lts
      - Explanation:
            - p 8080:808: Port 8080: This is where you will access the web interface.
            - p 50000:50000: Port 50000: Used for connecting distributed agents
            - -v jenkins_home:/var/jenkins_home: Volume: The -v flag ensures your configurations and jobs aren't deleted when the container stops.
            - -v //var/run/docker.sock:/var/run/docker.sock: Volume: we use the Docker Socket mapping—it lets Jenkins "reach out" of its own container to talk to the Docker engine on the Windows host.
1. Running permissions:
      - docker exec -u root jenkins-server chmod 666 /var/run/docker.sock
2. Accessing the Dashboard:
      - Once the container of Jenkins is running, open the web browser and in the address bar type: 
            - http://localhost:8080
      - Unlock Jenkins: On the first launch, Jenkins will ask for an Administrator password.
            + If using Docker: Look at your terminal logs; the password will be printed in a box.
            + If installed on Linux: Run sudo cat /var/lib/jenkins/secrets/initialAdminPassword.

3. The Setup Wizard
      - Once you enter the password, you'll see two options:
            - Install Suggested Plugins: Choose this one. It installs the basics like Git, Pipeline, and Gradle which you’ll need for your project.
            - Create Admin User: Set up your username and password so you don't have to use the long "initial password" every time

4. Pluggins:
- Once you are inside the dashboard, Go to Manage Jenkins > Plugins > Available Plugins.
- Search for and install "Docker Pipeline". This allows the Jenkinsfile we have in our directory to actually execute the sh 'docker-compose up' commands.


5. Put docker-compose inside the container (of jenkins):
      - docker exec -u root jenkins-server curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
      - docker exec -u root jenkins-server chmod +x /usr/local/bin/docker-compose

6. install docker CLI in the Jenkins container:
      - Enter the Jenkins container as root:
            - docker exec -u root -it jenkins-server bash

      - Install the Docker CLI:
            - apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
      curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      apt-get update && apt-get install -y docker-ce-cli

      - exit


+ closing the removing the containers:
      - docker compose -p kafka-tutorial-stack down