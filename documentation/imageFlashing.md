# Flashing the keychain backup image
Prerequisites:

Raspberry pi imager application installed, get it from here: https://www.raspberrypi.com/software/

SD card inserted into the computer

Image downloaded from our release page.

-----------


1. Run the pi imager application.
2. Click the Choose Device button.

![](pics/imager_choose_device.jpg)

3. Select your raspberry pi. I have a raspberry pi 3a+ so I've selected Raspberry Pi 3.

![](pics/imager_select_pi_list.jpg)

4. Back at the main screen click Choose OS.

![](pics/imager_choose_os.jpg)

5. Scroll down to the bottom and select Use Custom.

![](pics/imager_select_image_list.jpg)

6. Browse to the image file downloaded from our release page and click open.

![](pics/imager_select_image_picker.jpg)

9. Click Choose storage button.

![](pics/imager_choose_storage.jpg)

10. Select the SD card you have inserted.

![](pics/imager_select_sd_card.jpg)

12. Click the Next button.

![](pics/imager_all_selected_click_next.jpg)

13. A Customise OS screen will pop up. Click edit settings.

![](pics/imager_click_edit_settings.jpg)

14. On the General tab, Enter a hostname for the raspberry pi. This will make it easier to connect to later on. Also put in a username and password. You will need this later, so make a note of these values. Then set the wifi ssid and password.

![](pics/imager_os_customisation.jpg)

15. Click on the Services tab. Make sure Enable SSH is checked and Use password authentication is selected. Then click the save button.

![](pics/imager_os_customisation_services.jpg)

16. Click on Yes, apply settings.

![](pics/imager_click_yes_apply_settings.jpg)

17. A warning will pop up about overwriting data, verify the right device is selected and click Yes.

18. Once the Write has finished, remove the SD card from the computer and insert it into the Raspberry PI. You are now ready to do the hardware setup, [Hardware Assembly](assembly.md).
