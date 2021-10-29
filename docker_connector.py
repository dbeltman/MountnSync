import docker

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


def backupMount(source, destination):
    print("Backing up " + source + " To " + destination)
    volumeconfig={
        source: {'bind': '/source', 'mode': 'ro'},
        destination: {'bind': '/destination', 'mode': 'rw'}
        }
    try:
        backupcontainer = d.containers.run(
        "rclone/rclone",  
        "copy -P /source /destination",
        volumes=volumeconfig,
        name='rclone',
        remove=True,
        )
        print(backupcontainer)
    except Exception as exception:
        print(exception)
        print("Failed to run rclone container!")
        exit(1)