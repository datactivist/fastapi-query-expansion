. api-config.config     # Read config file

Help()
{
   # Display Help
   echo "Start expansion API service using api-config.config configuration."
   echo
   echo "Syntax: start_service.sh [-d|-s|-r|-h]"
   echo "options:"
   echo "d     Run the docker image on a container with the same name"
   echo "s     Run the docker image is silent mode (when using -d option)"
   echo "r     Run the API in reload mode (development)"
   echo "h     Show this help panel"
   echo
}

flag_start_docker=false
flag_silence_docker=false
flag_reload=false

while [ -n "$1" ]; do # while loop starts

	case "$1" in

    -d) flag_start_docker=true ;;

	-s) flag_silence_docker=true ;;

    -r) flag_reload=true ;;

    -h) Help 
        exit;;

	*) echo "Option $1 not recognized, use option -h to see available options" 
       exit;; # In case you typed a different option other than a,b,c

	esac

	shift

done

update_config()
{
    # ----- Modifying expansion.py -----
    if [ $deployment_method == "local" ]; then
        echo "Updating lexical_resources access in expansion.py"
        sudo sed -i "s/lexical_resources_API_host_name = .*/lexical_resources_API_host_name = '$lexical_resources_API_host_name'/" app/request_lexical_resources.py
        sudo sed -i "s/lexical_resources_API_port = .*/lexical_resources_API_port = '$lexical_resources_API_port'/" app/request_lexical_resources.py
        echo ""
    fi

}

start_docker()
{
    if $flag_start_docker; then
        sudo docker stop $docker_name
        sudo docker rm $docker_name
        if $flag_silence_docker; then
            sudo docker run -d --name $docker_name -h $expansion_API_host_name -p $expansion_API_port:80 $docker_name:$docker_version
        else
            sudo docker run --name $docker_name -h $expansion_API_host_name -p $expansion_API_port:80 $docker_name:$docker_version
        fi
    else
        echo "Not starting docker"
    fi
    echo ""
}

start_local_mode()
{
    cd app

    if $flag_reload; then
        uvicorn main:app --host $expansion_API_host_name --port $expansion_API_port --reload
    else
        uvicorn main:app --host $expansion_API_host_name --port $expansion_API_port
    fi

}

update_config
if [ $deployment_method == "local" ]; then
    start_local_mode
elif [ $deployment_method == "docker" ]; then
    sudo docker build -t $docker_name:$docker_version .
    start_docker
else
    echo "'$deployment_method' is not a valid value for deployment_method in config.config"
fi
