
# Fair-Billing | Fair Billable Session Report Generator | BT Technical Assessment

This Github Repository tracks the development of a Python tool to generate fair billable session reports. We also have a supporting config-driven Bash driver script and corresponding pytest unit tests.


## Installation & Execution Instructions


Step 1: Shallow-clone this Git Repository

```
git clone https://github.com/AbishekRajVG/SessionTracker_BT --depth 1 && cd SessionTracker_BT
```


Step 2: Use the driver script to operate this SessionTracker tool

```
./scripts/driver.sh -h
```


Step 3: Prepare the docker container

> **Pre-Requisite:** Please ensure the Docker daemon is running and the user is logged in using `docker login -u <USER>`


Set the required docker Image name and version in the config file

```
vim config/config.txt
```

Step 3.1: [Recommended] Pull the pre-built docker-image from Docker-Hub

```
./scripts/driver.sh -u
```

Step 3.2: [Alternatively] Build the docker image locally

```
./scripts/driver.sh -b
```

Step 4: Execute pytest Unit Test cases

```
./scripts/driver.sh -t
```


Step 5: Finally, Generate Fair Billable Session Reports

> **Note:** A fully-qualified file path must be provided

```
./scripts/driver.sh -f $PWD/input_sample_sessions.txt
```

---

  

## Intuition & Approach to the Solution

  
### Primary Goal

- The primary goal of this tool is to generate refined records of session information to fairly bill customers.
- Our source data is a haphazard Log file, and we’re to primarily extract valid logs of the format`TIMESTAMP CUSTOMER_NAME Start/End`
    
    ```bash
      14:02:03 ALICE99 Start
      14:02:05 CHARLIE End
      14:02:34 ALICE99 End
      14:02:58 ALICE99 Start
      14:03:02 CHARLIE Start
      14:03:33 ALICE99 Start
      14:03:35 ALICE99 End
      14:03:37 CHARLIE End
      14:04:05 ALICE99 End
      14:04:23 ALICE99 End
      14:04:41 CHARLIE Start
    ```
    
- Anomalies: There maybe END session entries without a corresponding START or Viseversa.
- The fair billable report must contain `user name`, `minimum possible sessions` , `minimum possible total session time`
- Logically, all valid session records will fall under one of these 5 scenarios:
    
    Case 1.1: New Customer normal start
    
    Case 1.2: New Customer but no matching start, Anomaly 1
    
    Case 2.1: Existing Customer Normal Start
    
    Case 2.2: Existing Customer but no matching start, Anomaly 2
    
    Case 2.3: Apart from per-line records, we also have to handle the edge case when a Customer is still active and has not Ended its session (after last known log)
    
- The prompt gives clear assumptions to overcome and suit each of these 5 scenarios

### Secondary Goal

- Make the app as light-weight as possible - meaning peak efficiency in both time and space
- Code coverage through pytest unit test cases for every function
- Containerised application - Since we have just a single easy tool, single container and no need of compose or kube orchestration
- Code Organisation
    - A primary Python tool to generate fair billable session reports. Break down into simple atomic functions
    - A corresponding pytest script to achieve high code coverage for all functions of the main tool
    - A config-driven driver script in Bash which gives us Command Line options to operate this tool
        - Config file which hosts docker image name and image version
        - BUILD docker images locally or PULL pre-built docker image
        - run pyTest unit test cases
        - Generate Fair Billable Session Reports passing source file as a CMD line argument

---

### My Approach

- A **layman** approach is to have two dictionaries. One for the number of sessions and another for the total session time
- A slightly better and more modular approach is Defining a class for Session (inheriting from) a class for customer - Let each session object has details per session record in logs. —> Impractical and complex
- The most obvious way to track enclosing sessions is by using a `Stack`  Data Structure
- The better way is to have only a single class for Customer
    - the customer object saves a `session stack` which persists START timestamps in the LIFO order
    - we then map the earliest END timestamp to the latest START timestamp - essentially pop() from the stack
The customer class saves the `active customer list` and `customer dict` at the class level. For the given scenario, all customers should be able to learn more about other active customers.
- `HH:MM:SS` time to epoch timestamps - easier to calculate the time difference in seconds

---

## Final Output from local test execution:

1. Perform a shallow clone from Git
2. Driver tool help
```
vgsabishekraj@simple-linux-vm:~/SessionTracker_BT$ ./scripts/driver.sh -h
This is the main driver script which drives this fair bill tool

Syntax: ./driver.sh [-h] [-u] [-b] [-t] [-f <source file path>]
options:

 -b           Build docker image locally
 -u           Pull docker image from remote Docker Hub
 -f FILE      Execute generate_billable_sessions tool with source log file
 -t           Run pytest testcases for the tool
 -h           Print this Help.
```
3. Prepare the docker container

    3.1. Pull pre-built docker image from docker-hub
    ```
    vgsabishekraj@simple-linux-vm:~/SessionTracker_BT$ ./scripts/driver.sh -u
    docker.io/vgsabishekraj/session-tracker-bt:v1.0
    vgsabishekraj/session-tracker-bt   v1.0      a7e3b5f704b2   19 hours ago   359MB
    ```
    
    3.2. Build the docker image locally
    
    ```
    vgsabishekraj@simple-linux-vm:~/SessionTracker_BT$ ./scripts/driver.sh -b
    [+] Building 1.7s (12/12) FINISHED                                                                                                                           docker:desktop-linux
     => [internal] load build definition from Dockerfile                                                                                                                         0.0s
     => => transferring dockerfile: 449B                                                                                                                                         0.0s
     => [internal] load .dockerignore                                                                                                                                            0.0s
     => => transferring context: 2B                                                                                                                                              0.0s
     => [internal] load metadata for docker.io/library/ubuntu:20.04                                                                                                              1.6s
     => [auth] library/ubuntu:pull token for registry-1.docker.io                                                                                                                0.0s
     => [1/6] FROM docker.io/library/ubuntu:20.04@sha256:0b897358ff6624825fb50d20ffb605ab0eaea77ced0adb8c6a4b756513dec6fc                                                        0.0s
     => [internal] load build context                                                                                                                                            0.0s
     => => transferring context: 319B                                                                                                                                            0.0s
     => CACHED [2/6] RUN apt-get update     && apt-get install -y         python3         python3-pip         bash         && rm -rf /var/lib/apt/lists/*                        0.0s
     => CACHED [3/6] RUN pip3 install pytest                                                                                                                                     0.0s
     => CACHED [4/6] WORKDIR /app                                                                                                                                                0.0s
     => CACHED [5/6] COPY ../scripts/generate_billable_sessions.py /app/                                                                                                         0.0s
     => CACHED [6/6] COPY ../tests/test_generate_billable_sessions.py /app/                                                                                                      0.0s
     => exporting to image                                                                                                                                                       0.0s
     => => exporting layers                                                                                                                                                      0.0s
     => => writing image sha256:fc70df9080524fbd29005147babf3e60344277aeac551f305a234bc22f736d88                                                                                 0.0s
     => => naming to docker.io/library/sess-tracker                                                                                                                              0.0s
     => => naming to docker.io/vgsabishekraj/session-tracker-bt:v1.0                                                                                                             0.0s
    ```
    
4. Execute pytest Unit Test cases
    
    ```
    vgsabishekraj@simple-linux-vm:~/SessionTracker_BT$ ./scripts/driver.sh -t
    vgsabishekraj/session-tracker-bt:v1.0
    ============================================================================== test session starts ===============================================================================
    platform linux -- Python 3.8.10, pytest-8.2.2, pluggy-1.5.0
    rootdir: /app
    collected 13 items                                                                                                                                                               
    
    test_generate_billable_sessions.py .............                                                                                                                           [100%]
    
    =============================================================================== 13 passed in 0.04s ===============================================================================
    ```
    

5.  Finally, Generate Fair Billable Session Reports
    
    ```
    vgsabishekraj@simple-linux-vm:~/SessionTracker_BT$ ./scripts/driver.sh -f /Users/abishek/Downloads/bt_test/SessionTracker_BT/input_sample_sessions.txt
    ALICE99 4 240
    CHARLIE 3 37
    ```
