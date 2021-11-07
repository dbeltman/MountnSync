import docker, yaml
from docker.api import container
from datetime import datetime
from os import getenv
from time import sleep
import json

d = docker.DockerClient(base_url='unix://var/run/docker.sock')


# Read YAML file
try:      
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
        print("Found config! Applying settings")
except:
    print("No (valid) config supplied, continuing without customization/configuration")

def listservices():
    list = d.services.list()
    return list

def getserviceidbyname(service_name):
    list = listservices()
    for service in list:
        if service.name == service_name:
            service_id = service.id
    return service_id

def getservicedetails(service_name):
    service_id = getserviceidbyname(service_name)
    service_details = d.services.get(service_id).tasks()
    # service_attrs = d.services.get(service_id).attrs
    # print(json.dumps(service_attrs, indent=4, sort_keys=True))
    return service_details

def getservicestate(service_name):
    service_details = getservicedetails(service_name)
    for task in service_details:
        if task['Status']['Message'] != "shutdown":
            service_state = "running"
            return service_state
    service_state = "shutdown"
    return service_state

def listcontainers():
    list = d.containers.list()
    return list

def containerdetails(name):
    details = d.containers.get(name)
    return details

def getContainerMounts(c_id, type):
    if type == 'container':
        mounts = d.containers.get(c_id).attrs['Mounts']
    elif type == 'service':
        mounts = d.services.get(getserviceidbyname(c_id)).attrs['Spec']['TaskTemplate']['ContainerSpec']['Mounts']
        print(mounts)
    else: 
        print("No (valid) type given")
        exit(1)
    return mounts

def containerCtl(c_id, action, type):
    try:
        print(action + " container " + c_id)
        if type == 'container':
            if action == 'stop':
                d.containers.get(c_id).stop()
            elif action == 'start':
                d.containers.get(c_id).start()
        elif type == 'service':
            if action == 'stop':
                d.services.get(getserviceidbyname(c_id)).scale(0)
                timeout = 0
                while getservicestate(c_id) == 'running':
                    if timeout < 30:
                        sleep(1)
                        print(c_id + " still " + getservicestate(c_id))
                        timeout += 1
                    else: 
                        print("Timed out waiting for " + c_id + " to stop")
            elif action == 'start':
                d.services.get(getserviceidbyname(c_id)).scale(1)
        else:
            print("No (valid) type given!")
            exit(1)
    except Exception as exception:
        print("Could not " + action + " container")
        print(exception)
        exit(1)


def makeBackup(hostSource, hostDestination, containerSource, containername):
    if containername in config:
        print("App config found for " + containername + " !")
        ignoredmounts = config[containername]['ignoredmounts']
        print(ignoredmounts)
    else:
        print("No app config found for " + containername + " !")
        ignoredmounts = []

    if hostSource in ignoredmounts or containerSource in ignoredmounts:
        print("Skipping backup of mount" + hostSource + ":" + containerSource + " as it was found in ignoredmounts list..")
    else:
        hostBackupDestination=hostDestination+"/"+containername+"/mounts"+containerSource
        print("Backing up " + hostSource + " To " + hostBackupDestination +"/..")
        volumeconfig={
            hostSource: {'bind': '/source', 'mode': 'ro'},
            hostBackupDestination: {'bind': '/destination', 'mode': 'rw'}
            }
        try:
            backupcontainer = d.containers.run(
            "rclone/rclone",  
            "copy -P /source /destination",
            volumes=volumeconfig,
            name='mountnsync-rclone',
            remove=True,
            )
            print(backupcontainer)
        except Exception as exception:
            print(exception)
            print("Failed to run rclone container!")
            exit(1)

def archiveBackup(containername, backuppath, archivepath):
    archivename=containername+"-"+datetime.today().strftime('%Y-%m-%d-%H%M%S')+".tar.gz"
    print("Archiving "+backuppath+" to "+archivepath+"/"+archivename+".tar.gz")
    volumeconfig={
        backuppath: {'bind': "/data", 'mode': 'rw'},
        archivepath: {'bind': '/destination', 'mode': 'rw'}
        }
    try:
        compresscontainer = d.containers.run(
        "alpine:3",  
        "tar -cvzf /destination/"+archivename+" /data",
        volumes=volumeconfig,
        name='mountnsync-compressor',
        remove=True,
        )
        print(compresscontainer)
    except Exception as exception:
        print(exception)
        print("Failed to run compression container!")
        exit(1)
