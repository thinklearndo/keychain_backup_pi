#/bin/python3
import time
from enum import Enum
import subprocess
import digitalio
import board
from adafruit_rgb_display import st7735
from PIL import Image, ImageDraw, ImageFont
import datetime
from collections import deque

class DriveState(Enum):
	NO_DRIVE = 1
	DRIVE_MOUNTING = 2
	DRIVE_MOUNTED = 3
	REMOVE_REQUESTED = 4
	MOUNT_FAILED = 5
	
class PortState(Enum):
	CLOSED = 1
	OPEN = 2
	
class BackupState(Enum):
	NOT_RUNNING = 1
	RUNNING = 2
	
class ButtonState(Enum):
	NO_ACTION = 1
	DOWN = 2
	CLICKED = 3

class ScreenState(Enum):
	OFF = 1
	ON = 2
	
class WifiState(Enum):
	DISCONNECTED = 1
	WAITING = 2
	CONNECTED = 3

def is_drive_available():
	result = subprocess.run(['ls', '/dev/'], stdout=subprocess.PIPE).stdout.decode('utf-8')
	
	for line in result.split('\n'):
		if "sda" in line:
			return True
	return False
	
def get_drive_location():
	result = subprocess.run(['mount'], stdout=subprocess.PIPE).stdout.decode('utf-8')
				
	for line in result.split('\n'):
		if "sda1" in line:
			return line.split()[2].strip()
	
	return ""

def is_drive_mounted():
	result = subprocess.run(['mount'], stdout=subprocess.PIPE).stdout.decode('utf-8')
				
	for line in result.split('\n'):
		if "sda1" in line:
			actualMountLocation = line.split()[2]
			return True

	return False

def is_wifi_connected():
	result = subprocess.run(['iwgetid', '--raw'], stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
	
	if len(result) == 0:
		# iwgetid --raw returns an empty string if not connected to a wifi network
		return False
	
	return True
	
def draw_image(display, image_file):
	image = Image.open(image_file)
	display.image(image)

def turn_on_screen(backlight_pin):
	backlight_pin.value = True
	return ScreenState.ON, time.time()

def turn_off_screen(backlight_pin):
	backlight_pin.value = False
	return ScreenState.OFF, -1

def is_usb_space_low(drive_location, low_disk_space_k):
	result = subprocess.run(['df', '-h', drive_location, '--output=avail', '-k'], stdout=subprocess.PIPE).stdout.decode('utf-8')
	
	free_space_int = int(result.split('\n')[1].rstrip())
	
	if (free_space_int <= low_disk_space_k):
		return True
	
	return False
	
def close_port():
	print("closing port")
	subprocess.run(['iptables', '-t', 'nat', '-F'])
	
	return PortState.CLOSED
	
def force_umount():
	subprocess.run(['systemctl', 'stop', 'sshd'])
	
	WaitForUnmountStartTimeSeconds = time.time()
			
	while is_drive_mounted() == True and time.time() - WaitForUnmountStartTimeSeconds <= 5:
	
		time.sleep(0.1)
		
		subprocess.run(['killall', 'sshd'])
	
		subprocess.run(['mount', '-f', '-o', 'remount,ro', '/dev/sda1'])
	
		subprocess.run(['umount', '/dev/sda1'])
		
	
	subprocess.run(['systemctl', 'start', 'sshd'])
	

def main():
	DefaultDriveMountLocation = "/media/usbdrive"
	ActualDriveMountLocation = ""
	ScreenOnTimeDelaySeconds = 15
	
	LowDiskSpaceWarningAmountK = 1000000 # 1 GB in KB
	LowDiskSpaceCheckDelaySeconds = 5
	LowDiskLastCheckTimeSeconds = 0

	CurrentDriveState = DriveState.NO_DRIVE
	CurrentPortState = PortState.CLOSED
	CurrentBackupState = BackupState.NOT_RUNNING
	CurrentWifiState = WifiState.WAITING
	CurrentLowDiskSpace = False
	
	Button1CurrentState = ButtonState.NO_ACTION
	Button2CurrentState = ButtonState.NO_ACTION
	
	CurrentScreenState = ScreenState.OFF
	ScreenTurnOnTimeSeconds = -1
	
	RemoveRequestStartTimeSeconds = -1
	RemoveRequestTimeLimitSeconds = 60
	ShouldCheckForRemoveRequest = False
	
	WaitForWifiStartTimeSeconds = time.time()
	WaitForWifiTimeLimitSeconds = 60
	
	DriveMountingStartTimeSeconds = -1
	DriveMountingTimeLimitSeconds = 12
	
	# this command runs top in the background in batch mode(-b) 2 samples(-n 2) with a 1 second delay between them (-d 1)
	TopStatsProcess = subprocess.Popen(['top', '-b', '-n', '2', '-d', '1'], stdout=subprocess.PIPE)
	sshdFoundQueue = deque()
	mmcWorkerFoundQueue = deque()
	
	#setup buttons
	button1 = digitalio.DigitalInOut(board.D18)
	button2 = digitalio.DigitalInOut(board.D27)

	button1.direction = digitalio.Direction.INPUT
	button1.pull = digitalio.Pull.UP

	button2.direction = digitalio.Direction.INPUT
	button2.pull = digitalio.Pull.UP
	#end button setup
	
	cs_pin = digitalio.DigitalInOut(board.CE0)
	dc_pin = digitalio.DigitalInOut(board.D25)
	reset_pin = digitalio.DigitalInOut(board.D24)
	backlight_pin = digitalio.DigitalInOut(board.D17)
	backlight_pin.direction = digitalio.Direction.OUTPUT
	BAUDRATE = 24000000
	
	spi = board.SPI()
	
	display = st7735.ST7735R(spi, rotation=90,
		cs=cs_pin,
		dc=dc_pin,
		rst=reset_pin,
		baudrate=BAUDRATE,
	)
	
	largeFont = font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
	
	image_folder = "/usr/share/keychain_manager/"
	usb_image = image_folder + "usb.jpg"
	usb_bad_image = image_folder + "usb_bad.jpg"
	usb_good_image = image_folder + "usb_good.jpg"
	usb_good_low_space_image = image_folder + "usb_good_no_space.jpg"
	usb_wait_image = image_folder + "usb_wait.jpg"
	blank_screen_image = image_folder + "blank.jpg"
	no_usb_idle_image = image_folder + "no_usb_idle.jpg"
	safe_to_remove_image = image_folder + "safe_to_remove.jpg"
	safe_to_remove_low_space_image = image_folder + "safe_to_remove_no_space.jpg"
	wifi_good_image = image_folder + "wifi_good.jpg"
	wifi_wait_image = image_folder + "wifi_wait.jpg"
	wifi_bad_image = image_folder + "wifi_bad.jpg"
	backup_running_image = image_folder + "backup_running.jpg"
	backup_running_low_space_image = image_folder + "backup_running_no_space.jpg"

	print("keychain manager started!")
	
	WaitForWifiStartTimeSeconds = time.time()
	
	while True:
		time.sleep(0.05) # sleep for 50 ms
		
		if button1.value == True and Button1CurrentState == ButtonState.DOWN:
			Button1CurrentState = ButtonState.CLICKED
		elif button1.value == False:
			Button1CurrentState = ButtonState.DOWN
			
		if button2.value == True and Button2CurrentState == ButtonState.DOWN:
			Button2CurrentState = ButtonState.CLICKED
		elif button2.value == False:
			Button2CurrentState = ButtonState.DOWN
		
		if ShouldCheckForRemoveRequest == True and Button1CurrentState == ButtonState.CLICKED:
		
			draw_image(display, usb_wait_image)
			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
		
			print("unmounting!")
			CurrentPortState = close_port()
			unmount_process = subprocess.run(['umount', '/dev/sda1'], stdout=subprocess.PIPE)
			
			WaitForUnmountStartTimeSeconds = time.time()
			
			while unmount_process.returncode != 0 and time.time() - WaitForUnmountStartTimeSeconds <= 5:
				time.sleep(0.05)
				unmount_process = subprocess.run(['umount', '/dev/sda1'], stdout=subprocess.PIPE)
				print("waiting for unmount success!")
			
			if time.time() - WaitForUnmountStartTimeSeconds > 5:
				print("force unmounting!")
				force_umount()
			
			draw_image(display, safe_to_remove_image)
			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
			CurrentDriveState = DriveState.REMOVE_REQUESTED
			RemoveRequestStartTimeSeconds = time.time()
			ShouldCheckForRemoveRequest = False
		elif ShouldCheckForRemoveRequest == True and CurrentScreenState == ScreenState.OFF:
			ShouldCheckForRemoveRequest = False

		if CurrentDriveState == DriveState.DRIVE_MOUNTED and time.time() - LowDiskLastCheckTimeSeconds > LowDiskSpaceCheckDelaySeconds:
			CurrentLowDiskSpace = is_usb_space_low(ActualDriveMountLocation, LowDiskSpaceWarningAmountK)
			LowDiskLastCheckTimeSeconds = time.time()
			
		if TopStatsProcess.poll() != None:
			# process finished, get some info for checking if a backup is running
			
			if CurrentDriveState == DriveState.DRIVE_MOUNTED:
			
				lineCount = 0
				foundSshd = False
				foundMmcWorker = False
				
				for line in TopStatsProcess.communicate()[0].decode('utf-8').split('\n'):
					# sshd and mmc worker should be in the top 15 lines of tops output
					# don't even need to check cpu usage, if they are there, they are doing work
					lineCount = lineCount + 1
					
					if "sshd" in line:
						#print(line)
						foundSshd = True
					
					if "mmc" in line:
						#print(line)
						foundMmcWorker = True
					
					if lineCount > 15:
						break
						
				
				sshdFoundQueue.append(foundSshd)
				mmcWorkerFoundQueue.append(foundMmcWorker)
				
				if len(sshdFoundQueue) > 5:
					sshdFoundQueue.popleft()
					mmcWorkerFoundQueue.popleft()
				
				sshdCount = 0
				mmcCount = 0
				for item in sshdFoundQueue:
					if item == True:
						sshdCount = sshdCount + 1
				
				for item in mmcWorkerFoundQueue:
					if item == True:
						mmcCount = mmcCount + 1
						
				mountBusy = False
				
				mountUsageResult = subprocess.run(['fuser', '-m', '/dev/sda1'], stdout=subprocess.PIPE).stdout.decode('utf-8')
				
				for line in mountUsageResult.split('\n'):
					if "sda1" in line:
						mountBusy = True
				
				# at least 2 Trues and we'll say a backup is running
				if sshdCount >= 2 or mmcCount >= 2 or mountBusy == True:
					CurrentBackupState = BackupState.RUNNING
				else:
					CurrentBackupState = BackupState.NOT_RUNNING
			
			#start the stats process again
			TopStatsProcess = subprocess.Popen(['top', '-b', '-n', '2', '-d', '1'], stdout=subprocess.PIPE)
				
		
		wifiCheckResult = is_wifi_connected()
		
		if CurrentWifiState != WifiState.CONNECTED and wifiCheckResult == True:
			CurrentWifiState = WifiState.CONNECTED
			WaitForWifiStartTimeSeconds = -1
			draw_image(display, blank_screen_image)
			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
			draw_image(display, wifi_good_image)
		
		if CurrentWifiState == WifiState.WAITING and time.time() - WaitForWifiStartTimeSeconds > WaitForWifiTimeLimitSeconds:
			CurrentWifiState = WifiState.DISCONNECTED
			WaitForWifiStartTimeSeconds = -1
			draw_image(display, blank_screen_image)
			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
			draw_image(display, wifi_bad_image)
		
		if CurrentWifiState == WifiState.CONNECTED and wifiCheckResult == False:
			CurrentWifiState = WifiState.DISCONNECTED
			WaitForWifiStartTimeSeconds = -1
			draw_image(display, blank_screen_image)
			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
			draw_image(display, wifi_bad_image)
		
		if CurrentDriveState == DriveState.NO_DRIVE:
			if is_drive_available() == True and is_drive_mounted() == False:
					
				print("found drive, but not mounted... Mounting")
				draw_image(display, blank_screen_image)
				
				CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
			
				draw_image(display, usb_wait_image)
				
				subprocess.run(['mkdir', '-p', DefaultDriveMountLocation], stdout=subprocess.PIPE)
				
				#check if its ext* filesystem
				isVfat = True
				filesysteminfo = subprocess.run(['file', '-sL', '/dev/sda1'], stdout=subprocess.PIPE).stdout.decode('utf-8')
				for line in filesysteminfo.split('\n'):
					if "ext" in line:
						isVfat = False
			
				if isVfat == True:
					subprocess.Popen(['mount', '-o', 'uid=1000,gid=1000', '/dev/sda1', DefaultDriveMountLocation])
				else:
					subprocess.Popen(['mount', '/dev/sda1', DefaultDriveMountLocation])
			
				CurrentDriveState = DriveState.DRIVE_MOUNTING
				DriveMountingStartTimeSeconds = time.time()
				
			elif is_drive_available() == True and is_drive_mounted() == True:
				ActualDriveMountLocation = get_drive_location()
				print("Drive mounted at", ActualDriveMountLocation)
				CurrentDriveState = DriveState.DRIVE_MOUNTED
		
		elif CurrentDriveState == DriveState.DRIVE_MOUNTING:
			print("checking if its mounted yet...")
			if is_drive_mounted() == True:
				print("Yay its mounted!")
				ActualDriveMountLocation = get_drive_location()
				CurrentDriveState = DriveState.DRIVE_MOUNTED
			
			if time.time() - DriveMountingStartTimeSeconds > DriveMountingTimeLimitSeconds:
				CurrentDriveState = DriveState.MOUNT_FAILED
				draw_image(display, blank_screen_image)
				draw_image(display, usb_bad_image)
				CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
				DriveMountingStartTimeSeconds = -1
		
		elif CurrentDriveState == DriveState.REMOVE_REQUESTED:
			if is_drive_available() == False and is_drive_mounted() == False:
				CurrentDriveState = DriveState.NO_DRIVE
				draw_image(display, blank_screen_image)
				draw_image(display, no_usb_idle_image)
				CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)
			elif time.time() - RemoveRequestStartTimeSeconds > RemoveRequestTimeLimitSeconds:
				CurrentDriveState = DriveState.NO_DRIVE
				RemoveRequestStartTimeSeconds = -1
	
		elif CurrentDriveState == DriveState.MOUNT_FAILED:
			if is_drive_available() == False:
				CurrentDriveState = DriveState.NO_DRIVE
		
		elif CurrentDriveState == DriveState.DRIVE_MOUNTED:
			#check if drive is unexpectedly removed
			if is_drive_available() == False:
				if is_drive_mounted() == True:
					force_umount()
			
				print("drive unexpectedly removed")
				CurrentDriveState = DriveState.NO_DRIVE
		
		if CurrentDriveState == DriveState.DRIVE_MOUNTED and CurrentPortState == PortState.CLOSED:
			with open('/proc/sys/net/ipv4/ip_forward', "w") as ip_forward_file:
				subprocess.run(['echo', '1'], stdout=ip_forward_file)

			subprocess.run(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-p', 'tcp', '--dport', '2222', '-j', 'REDIRECT', '--to-port', '22'])
			CurrentPortState = PortState.OPEN
			
			CurrentLowDiskSpace = is_usb_space_low(ActualDriveMountLocation, LowDiskSpaceWarningAmountK)
			
			draw_image(display, blank_screen_image)
			
			if CurrentLowDiskSpace == True:
				print("mounted low disk space")
				draw_image(display, usb_good_low_space_image)
					
			else:
				print("mounted plenty of disk space")
				draw_image(display, usb_good_image)

			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)

		elif CurrentDriveState != DriveState.DRIVE_MOUNTED and CurrentPortState == PortState.OPEN:
			CurrentPortState = close_port()

		if CurrentScreenState == ScreenState.OFF and (Button1CurrentState == ButtonState.CLICKED or Button2CurrentState == ButtonState.CLICKED):
			draw_image(display, blank_screen_image)

			if CurrentWifiState == WifiState.WAITING:
				print("showing wifi waiting")
				draw_image(display, wifi_wait_image)
			elif CurrentWifiState == WifiState.DISCONNECTED:
				print("showing wifi bad")
				draw_image(display, wifi_bad_image)
			elif CurrentDriveState == DriveState.MOUNT_FAILED:
				print("showing bad drive")
				draw_image(display, usb_bad_image)
			elif CurrentDriveState == DriveState.NO_DRIVE:
				print("showing idle")
				draw_image(display, no_usb_idle_image)
			elif CurrentDriveState == DriveState.DRIVE_MOUNTING:
				print("showing mounting")
				draw_image(display, usb_wait_image)
			elif CurrentBackupState == BackupState.RUNNING:
				if CurrentLowDiskSpace == True:
					print("backup running low disk space")
					draw_image(display, backup_running_low_space_image)
					
				else:
					print("backup running")
					draw_image(display, backup_running_image)
				
				ShouldCheckForRemoveRequest = True
				
			elif CurrentDriveState == DriveState.DRIVE_MOUNTED and CurrentBackupState == BackupState.NOT_RUNNING:
				print("unmounting!")
				
				CurrentPortState = close_port()
				
				subprocess.run(['umount', '/dev/sda1'], stdout=subprocess.PIPE)
				
				if is_drive_mounted() == True:
					force_umount()
				
				if CurrentLowDiskSpace == True:
					print("showing safe to remove low space")
					draw_image(display, safe_to_remove_low_space_image)
					
				else:
					print("showing safe to remove")
					draw_image(display, safe_to_remove_image)

				CurrentDriveState = DriveState.REMOVE_REQUESTED
				RemoveRequestStartTimeSeconds = time.time()
				print("drivestate = ", CurrentDriveState)
			elif CurrentDriveState == DriveState.REMOVE_REQUESTED:
				if CurrentLowDiskSpace == True:
					print("showing safe to remove low space")
					draw_image(display, safe_to_remove_low_space_image)
					
				else:
					print("showing safe to remove")
					draw_image(display, safe_to_remove_image)

			CurrentScreenState, ScreenTurnOnTimeSeconds = turn_on_screen(backlight_pin)

		if Button1CurrentState == ButtonState.CLICKED:
			print("button1 clicked!")
			Button1CurrentState = ButtonState.NO_ACTION
			
		if Button2CurrentState == ButtonState.CLICKED:
			print("button2 clicked!")
			Button2CurrentState = ButtonState.NO_ACTION

		if CurrentScreenState == ScreenState.ON:
			if time.time() - ScreenTurnOnTimeSeconds > ScreenOnTimeDelaySeconds:
				CurrentScreenState, ScreenTurnOnTimeSeconds = turn_off_screen(backlight_pin)
				draw_image(display, blank_screen_image)
if __name__ == "__main__":
    main()

