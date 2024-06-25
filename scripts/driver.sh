#/bin/bash

# read config file
relative_path="$(dirname "$0")"

source ${relative_path}/../config/config.txt

get_help()
{
    # Display Help
    echo "This is the main driver script which drives this fair bill tool"
    echo
    echo "Syntax: ./driver.sh [-h] [-u] [-b] [-t] [-f <source file path>]"
    echo "options:"
    echo
    echo " -b           Build docker image locally"
    echo " -u           Pull docker image from remote Docker Hub"
    echo " -f FILE      Execute generate_billable_sessions tool with source log file"
    echo " -t           Run pytest testcases for the tool"
    echo " -h           Print this Help."
    echo
}

############################################################
############################################################
# Main program                                             #
############################################################
############################################################

log_file=""

run_pytest(){
    echo  "${DOCKER_IMAGE}:${IMAGE_VER}"
    docker run -t "${DOCKER_IMAGE}:${IMAGE_VER}" python3 -m pytest /app/ 
}

update_image(){
    docker pull ${DOCKER_IMAGE}:${IMAGE_VER} -q
}

build_local(){
    docker build -t sess-tracker . -f ${relative_path}/../docker/Dockerfile -t "${DOCKER_IMAGE}:${IMAGE_VER}"
}

run_generate_billable_sessions(){
    eval "docker run -v ${log_file}:/app/session.log -t ${DOCKER_IMAGE}:${IMAGE_VER} python3 /app/generate_billable_sessions.py /app/session.log"
}

# Get the options
while getopts ":hubtf:" option; do
    case $option in
        h)  get_help
            exit;;
        t)  run_pytest
            exit;;
        u)  update_image
            docker images | grep "${DOCKER_IMAGE}.*.${IMAGE_VER}"
            exit;;
        b)  build_local
            exit;;
        f)  log_file=$(echo "$OPTARG" | sed 's/ /\\ /g')
            if [[ -z "$log_file" ]]; then
                echo "Error: Missing argument for -f option."
                exit 1
            fi
            run_generate_billable_sessions
            exit;;
        \?) # Invalid option
            echo "Error: Invalid option. Please execute ./driver.sh -h for valid options."
            exit;;
    esac
done












