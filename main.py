import docker_connector, json, argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument("container", type=str, metavar='container', help="Name or ID of Container")
parser.add_argument("-b", "--backup", type=str, help = "Make a backup of the container mount(s), usage: 'all' or </mount/in/target/container> (todo)")
parser.add_argument("-d", "--destination", type=str, help = "/host/destination/path")
parser.add_argument("-i", "--details", type=str, help = "Get detail of Container, usage: 'all', 'mounts'")
args= parser.parse_args()

if args.container == "all":
    list = docker_connector.listcontainers()
    print(str(list))

elif args.details:
    if args.details == 'all':
        detailsample = docker_connector.containerdetails(args.container)
        print(str(args.container))
        print(str(detailsample))
    elif args.details == 'mounts':
        print(str(args.container))
        mounts = docker_connector.getContainerMounts(args.container)
        for mount in mounts:
            print(mount['Source'] + ":" + mount['Destination'])

elif args.backup:
    if args.destination:
        docker_connector.containerCtl(args.container, "stop")
        if args.backup == 'all':
            mounts = docker_connector.getContainerMounts(args.container)
            for mount in mounts:
                docker_connector.backupMount(mount['Source'], args.destination)
        docker_connector.containerCtl(args.container, "start")
    else:
        print("No destination given!")
        exit(1)

