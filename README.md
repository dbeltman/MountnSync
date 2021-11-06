# Mount-n-Sync
Docker container (bind-) mount discovery and backup tool

### What does this do?

- Discover bind mounts attached to a specified container or service
- Back up these bind mounts to a destination of your choosing
- Gracefully shuts down the container/service before backing up, and starts it up again after backing up
- (Optionally) Archive the backup so it is stored in a timestamped .tar.gz file for easy organising
- Allows for exluding mounts via config.yaml

### How does it do that?

- Discovery is done using the Docker Socket (/var/run/docker.sock)
- Backup of files is done by spinning up an rclone container, whilst (read-only) binding the specified container's mounts as a source. 
- Destination folder is overwritten if contents have changed, will not touch anything else
- Archival is done using `tar` on an alpine container, binding the finished backup as a source and writing it to the same location as $containername-$timestamp.tar.gz 

### How do i use it?

##### (Optional) creating a config file
There is a `config.dist.yaml` file included that serves as an example of what the config can do. Copy it to `config.yaml` and mount it accordingly to enable it.

By default `--backup all` will scan for all mounts and back them up. You can ignore certain mounts, so they wont be backed up. 
For example:
 - Plex media library
 - Some app that has a (large) database you dont necessarily need
TODO: Exlude certain folders/files in mount using the rclone exclude command. For now this supports only whole mounts.
Large files along config files in the same mount will require you to separate those files/folders into further container mounts

##### Creating a simple folder backup
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --name mountnsync \
    dockerdaan/mountnsync:latest \
    --backup all --type container --destination /your/backup/location <containername>
```
> This will create a backup of all $containername mounts in /your/backup/location/$containername/mounts/{$mount1,$mount2,etc..}

##### Creating a backup and archiving it
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --name mountnsync \
    dockerdaan/mountnsync:latest \
    --backup all --type container --destination --archive /your/backup/location <containername>
```
> The --archive flag will create an archive of the latest backup in /your/backup/location/$containername/archives/$containername$timestamp.tar.gz

##### Creating a backup of a service, using config.yaml
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /your/config.yaml:/app/config.yaml \
    --name mountnsync \
    dockerdaan/mountnsync:latest \
    --backup all --type service --destination --archive /your/backup/location <servicename>_<taskname>
```
> The --archive flag will create an archive of the latest backup in /your/backup/location/$containername/archives/$containername$timestamp.tar.gz