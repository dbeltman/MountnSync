import docker
from datetime import datetime

d = docker.DockerClient(base_url='unix://var/run/docker.sock')

def listcontainers():
    list = d.containers.list()
    return list

def containerdetails(name):
    details = d.containers.get(name)
    return details

def getContainerMounts(c_id):
    mounts = d.containers.get(c_id).attrs['Mounts']
    return mounts

def containerCtl(c_id, action):
    try:
        print(action + " container " + c_id)
        if action == 'stop':
            d.containers.get(c_id).stop()
        elif action == 'start':
            d.containers.get(c_id).start()
    except Exception as exception:
        print("Could not " + action + " container")
        print(exception)
        exit(1)


def makeBackup(hostSource, hostDestination, containerSource, containername):
    hostBackupDestination=hostDestination+"/"+containername+containerSource
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

def archiveBackup(hostBackupPath, hostDestination, containername):
    archivename=containername + "-" + datetime.today().strftime('%Y-%m-%d-%H%M%S')
    print("Archiving " + hostBackupPath + " to " + hostDestination + "/"+ archivename)
    volumeconfig={
        hostBackupPath: {'bind': "/"+containername, 'mode': 'rw'},
        hostDestination: {'bind': '/destination', 'mode': 'rw'}
        }
    try:
        compresscontainer = d.containers.run(
        "alpine:3",  
        "tar cvzf /destination/"+ archivename +".tar.gz /"+containername,
        volumes=volumeconfig,
        name='mountnsync-compressor',
        remove=True,
        )
        print(compresscontainer)
    except Exception as exception:
        print(exception)
        print("Failed to run compression container!")
        exit(1)