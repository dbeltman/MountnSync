# Mount-n-Sync
Docker container (bind-) mount discovery and backup tool

### What does this do?

- Discover bind mounts attached to a specified container
- Back up these bind mounts to a destination of your choosing
- (Optionally) Archive the backup so it is stored in a timestamped .tar.gz file for easy organising

### How does it do that?

- Discovery is done using the Docker Socket (/var/run/docker.sock)
- Backup of files is done by spinning up an rclone container, whilst (read-only) binding the specified container's mounts as a source. 
- Destination folder is overwritten if contents have changed, will not touch anything else
- Archival is done using `tar` on an alpine container, binding the finished backup as a source and writing it to the same location as $containername-$timestamp.tar.gz 

### How do i use it?

##### Creating a simple folder backup
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --name mountnsync \
    dockerdaan/mountnsync:latest \
    main.py --backup all --destination /your/backup/location <containername>
```
> This will create a backup of all <containername> mounts in /your/backup/location/<containername>/mounts/{<mount1>,<mount2>,etc..}

##### Creating a backup and archiving it
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --name mountnsync \
    dockerdaan/mountnsync:latest \
    main.py --backup all --destination --archive /your/backup/location <containername>
```
> The --archive flag will create an archive of the latest backup in /your/backup/location/<containername>/archives/<containername><timestamp>.tar.gz