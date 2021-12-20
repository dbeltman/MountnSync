from os import wait, getenv
from time import sleep
import docker_connector, json, argparse, sys

# Main Args
parser = argparse.ArgumentParser()
parser.add_argument("container", type=str, metavar='container', help="Name or ID of Container")
parser.add_argument("-b", "--backup", type=str, help = "Make a backup of the container mount(s), usage: 'all' or </mount/in/target/container> (todo)")
parser.add_argument("-d", "--destination", type=str, help = "/host/destination/path")
parser.add_argument("-t", "--type", type=str, help = "Container type, usage: 'service' or 'container'")

# Secondary (test) args
parser.add_argument("-i", "--details", type=str, help = "Get detail of Container, usage: 'all', 'mounts'")
parser.add_argument("-l", "--list", type=str, help = "List either 'containers' or 'services'")
parser.add_argument("-s", "--scale", type=str, help = "Scale Service")

# Flags
parser.add_argument("-a", "--archive", action='store_true', help="Archive the backup location afterwards. /destination/<containername>/all/your/data will be stored in /destination/<containername><todaysdate>.tar.gz")
parser.add_argument("-sd", "--servicedetails", action='store_true', help="Show service details of the given container")

# Parse Args
args= parser.parse_args()

# Timeout in seconds to wait for the container/service to stop running
stop_timeout = getenv('STOPTIMEOUT', "30")

if args.list == "services":
    list = docker_connector.listservices()
    for service in list:
        print(str(service.name))
        print(json.dumps(service.attrs[''], indent=4, sort_keys=True))
    print(str(list))
elif args.servicedetails:
    details =  docker_connector.getservicedetails(args.container)
    # print(json.dumps(details, indent=4, sort_keys=True))
elif args.scale:
    service_id = docker_connector.getserviceidbyname(args.container)
    test = docker_connector.scaleservice(service_id, int(args.scale))
    print(test)
    service_state = docker_connector.getservicestate(args.container)
    print(service_state)
    timeout = 0
    while docker_connector.getservicestate(args.container) == 'running':
        if timeout < int(stop_timeout):
            sleep(1)
            service_state = docker_connector.getservicestate(args.container)
            print(service_state)
            timeout += 1
        else:
            print("Timed out waiting for " + args.container + " to scale down.")
            exit(1)

elif args.details:
    if args.details == 'all':
        detailsample = docker_connector.containerdetails(args.container)
        print(str(args.container))
        print(str(detailsample))
    elif args.details == 'mounts':
        print(str(args.container))
        mounts = docker_connector.getContainerMounts(args.container, args.type)
        for mount in mounts:
            if args.type == 'container':
                print(mount['Source'] + ":" + mount['Destination'])
            elif args.type == 'service':
                #TODO named volume support
                print(mount['Source'] + ":" + mount['Target'])

elif args.backup:
    if args.destination:
        # Stop our container or scale down service
        docker_connector.containerCtl(args.container, "stop", args.type)
        if args.backup == 'all':
            mounts = docker_connector.getContainerMounts(args.container, args.type)
            print(mounts)
            for mount in mounts:
                if args.type =='container':
                    docker_connector.makeBackup(mount['Source'], args.destination, mount['Destination'], args.container)
                elif args.type == 'service':
                    #TODO named volume support
                    print("Backing up " + mount['Source'] + " to " + args.destination)
                    docker_connector.makeBackup(mount['Source'], args.destination, mount['Target'], args.container)
                else:
                    print("No (valid) type given")
        # Start our container or scale up service
        docker_connector.containerCtl(args.container, "start", args.type)
        if args.archive == True:
            print("Archiving backup")
            archivePath=args.destination+"/"+args.container+"/archives"
            backupPath=args.destination+"/"+args.container+"/mounts"
            docker_connector.archiveBackup(args.container, backupPath, archivePath)
        else:
            print("Not archiving backup..")

    else:
        print("No destination given!")
        exit(1)

