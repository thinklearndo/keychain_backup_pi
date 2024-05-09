## Using FolderSync app to sync files from Android to keychain backup

Before running this setup doc, make sure the USB drive is inserted into your Keychain backup device.

Install FolderSync app from the Play Store.

-----

1. Click create folderpair button.

![](pics/foldersync_create_folderPair.jpg)

2. Give the folderpair a name and click next.

![](pics/foldersync_name_folderpair.jpg)

3. Leave Sync engine v2 selected and click next.

![](pics/foldersync_sync_engine.jpg)

4. Select To right folder and click next.

![](pics/foldersync_sync_type_screen.jpg)

5. On the Sync folders click on Select folder under Left folder.

![](pics/foldersync_left_side_select_folder.jpg)

6. Select the folder to be backed up. For pictures and videos on Android, that would be the DCIM folder. Then click Select.

![](pics/foldersync_select_dcim.jpg)

7. Back at the Sync folders screen, under Right folder click on SD CARD.

![](pics/foldersync_right_folder_select_sd_card.jpg)

8. Click Add account.

![](pics/foldersync_right_folder_add_account.jpg)

9. Scroll to the bottom and select SFTP under File protocols.

![](pics/foldersync_right_folder_click_sftp.jpg)

10. Click on the little pencil in the upper right corner and give the account a name.

![](pics/foldersync_sftp_name.jpg)

11. Under login, enter the username and password you used to setup the raspberry pi.

![](pics/foldersync_enter_username_and_password.jpg)

12. Under Connection, in the server address box, put in the IP address or host name of the keychain backup device and in the Port box put 2222.

![](pics/foldersync_hostname_and_port.jpg)

13. Once all the info has been entered, click the back arrow in the upper left corner.

![](pics/foldersync_host_created_click_back.jpg)

14. Back at the Sync folders screen, click on the SD CARD button under Right folder again. Select the newly created host.

![](pics/foldersync_right_select_new_sftp_account.jpg)

15. In the Select folder window, click media, then click usbdrive.

![](pics/foldersync_select_media_folder.jpg)

16. Then click the Add folder button in the lower right corner.

![](pics/foldersync_create_usb_drive_folder.jpg)

17. In the create folder screen, enter a descriptive name for this backup storage location. This will allow mulitple android devices to backup to this USB drive.

![](pics/foldersync_name_folder_on_usb.jpg)

18. Then click on the newly created folder.

![](pics/foldersync_select_created_usb_folder.jpg)

19. Finally click on Select button.

![](pics/foldersync_finally_select_usb_folder.jpg)

20. Then click Next on the Sync folders screen.

![](pics/foldersync_click_next_on_sync_folders.jpg)

21. Then click save.

![](pics/foldersync_save_create_folderpair.jpg)

22. To run the sync operation, click Sync.

![](pics/foldesync_run_sync.jpg)

23. To schedule syncs, click the Scheduling button.

![](pics/foldesync_schedule_sync.jpg)

24. Then click + schedule.

25. After setting up the schedule click save.

26. To verify that files are syncing, after the sync finishes, safely remove the usb drive and plug it into a computer. Open a file browser window and go to the usb device folder. Verify that the expected files are there.


