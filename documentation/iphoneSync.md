### Setting up syncing for iPhone
----

Steps:

1. Install PhotoBackup from the app store (https://apps.apple.com/us/app/photobackup-backup-photos-and-videos-via-rsync/id945026388)

2. Allow PhotoBackup to connect to devices on your local network.

![](pics/iphone_allow_network_access.jpg)

3. Click on Computer and enter in the hostname or IP address of your keychain backup device.

![](pics/iphone_enter_ip_address.jpg)

4. Enter your SSH credentials for your raspberry pi.

![](pics/iphone_enter_ssh_credentials.jpg)

5. For remote folder enter /media/usbdrive

![](pics/iphone_enter_remote_folder.jpg)

6. Allow PhotoBackup to access your photos.

![](pics/iphone_allow_photo_access.jpg)

7. Click Backup Camera Roll to backup your photos and videos to keychain backup.

![](pics/iphone_start_backup.jpg)
