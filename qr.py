import cv2
import time
import os
import subprocess
import sys
from pyzbar.pyzbar import decode
import gpio as GPIO
import pyttsx3

sys.path.insert(0, '/home/rock/Desktop/Hearsight/')
from config import *
from play_audio import GTTSA

# Define global variables
essids = []  # List to store ESSIDs of available WiFi networks

# Initialize GPIO
GPIO.setup(450, GPIO.IN)  # Forward button
GPIO.setup(421, GPIO.IN)  # Backward button
GPIO.setup(447, GPIO.IN)  # Feature button

# Initialize text-to-speech engine
engine = pyttsx3.init()
# engine.setProperty('voice', 'english_rp+f3')
# engine.setProperty('rate', 120)
engine.setProperty('voice', 'en-gb')
engine.setProperty('rate', 140)
play_file = GTTSA()

file_path = '/home/rock/Desktop/Hearsight/network.txt'

def find_wireless_interface():
    try:
        result = os.popen('iw dev | grep Interface').read()
        interface = result.split(' ')[1].strip()
        return interface
    except Exception as e:
        print(f"An error occurred while finding the wireless interface: {e}")
        play_file.play_audio_file("no_WiFi_networks_found_enable_mobile_hotspot_and_try_again.mp3")
        time.sleep(0.3)
        sys.exit()

def extract_essids(result):
    return [line.split('"')[1] for line in result.split('\n') if 'ESSID' in line]

#def connect_to_wifi(ssid, data):
#    os.system(f"nmcli device wifi connect '{ssid}' password '{data}'")
#    print('CONNECTED TO YOUR NETWORK SUCCESSFULLY')
#    return True

def connect_to_wifi(ssid, data):
#    os.system(f"nmcli device wifi connect '{ssid}' password '{data}'")

    # Construct the nmcli command with placeholders for SSID and password
    command = f"nmcli device wifi connect '{ssid}' password '{data}'"

    # Run the command and capture the output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip() == "Error: Connection activation failed: (7) Secrets were required, but not provided.":
        error_message = result.stdout.strip()
        print(error_message)
        print("password not suitable for this selected ssid")
        capture_qr_code_if_incorrect(ssid)
        check_selected_essid_in_file(ssid, file_path)
#        print('<<<<<<<SUCCESSFULLY>>>>>>')
#        sys.exit()
    else:
        print('CONNECTED TO YOUR NETWORK SUCCESSFULLY')
        
def capture_qr_code_if_incorrect(ssid):
    # Open the default camera (you can also specify a specific camera using the index)
    cap = cv2.VideoCapture(1)

    # Get the current time
    start_time = time.time()

    while time.time() - start_time < 10:  # Capture images for 10 seconds
        # Read a frame from the camera
        ret, frame = cap.read()

        # Display the frame
        cv2.imshow('Camera', frame)

        # Press 'q' to break out of the loop before 10 seconds
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()

    # Convert the last captured frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use pyzbar to decode the QR code
    decoded_objects = decode(gray)

    # Print the decoded information
    if decoded_objects:
        data = decoded_objects[0].data.decode('utf-8')
        #print(data)
#        b=data.split('|')
        #print(b)
#        data=b[1]
        data = data.split('|')[1].strip()
        print(data)
        print(f'QR Code Data: {data}')
        
        # Define the content to write to the file
#        content = f'ssid = "{ssid}"\npassword = "{password}"'
        content = f'ssid = "{ssid}" password = "{data}"\n'

        # Write the content to the file
        with open(file_path, 'a') as file:
            file.write(content)
    
        # Define the file path
#        file_path = '/home/rock/Desktop/Hearsight/network.txt'

        # Initialize an empty dictionary to store the latest occurrence of each SSID
        ssid_passwords = {}
       
        # Read the input data from the specified text file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Process each line of data
        for line in lines:
            ssid = line.split('ssid = "')[1].split('"')[0]  # Extract the SSID
            password = line.split('password = "')[1].split('"')[0]  # Extract the password
            ssid_passwords[ssid] = password  # Store the latest occurrence of each SSID
        
        # Write the unique SSID-password pairs back to the same file
        with open(file_path, 'w') as file:
            for ssid, password in ssid_passwords.items():
                file.write(f'ssid = "{ssid}" password = "{password}"\n')

    else:
        print('No....... QR code detected in the captured image.')

def capture_qr_code():
    # Open the default camera (you can also specify a specific camera using the index)
    cap = cv2.VideoCapture(1)

    # Get the current time
    start_time = time.time()

    while time.time() - start_time < 10:  # Capture images for 10 seconds
        # Read a frame from the camera
        ret, frame = cap.read()

        # Display the frame
        cv2.imshow('Camera', frame)

        # Press 'q' to break out of the loop before 10 seconds
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()

    # Convert the last captured frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use pyzbar to decode the QR code
    decoded_objects = decode(gray)

    # Print the decoded information
    if decoded_objects:
        data = decoded_objects[0].data.decode('utf-8')
        #print(data)
#        b=data.split('|')
        #print(b)
#        data=b[1]
        data = data.split('|')[1].strip()
        print(data)
        print(f'QR Code Data: {data}')
        
        # Define the content to write to the file
#        content = f'ssid = "{ssid}"\npassword = "{password}"'
        content = f'ssid = "{ssid}" password = "{data}"\n'

        # Write the content to the file
        with open(file_path, 'a') as file:
            file.write(content)
        connect_to_wifi(ssid, data)
        sys.exit()

    else:
        print('No QR code detected in the captured image.')

#def check_selected_essid_in_file(ssid):
#    try:
#        with open(file_path, 'r') as file:
#            lines = file.readlines()
#            for line in lines:
#                if ssid in line:
#                    ssid = line.split('ssid = "')[1].split('"')[0]
#                    password = line.split('password = "')[1].split('"')[0]
#                    print(f"SSID: {ssid}, Password: {password}")
#                    print(ssid)
#                    print(password)
#                    data = password
#                    connect_to_wifi(ssid, data)
#                    sys.exit()
#            else:
#                print("No, ssid is not present in the file.")
#                capture_qr_code()
#    except FileNotFoundError:
#        print("File not found.")
#    except Exception as e:
#        print(f"An error occurred while reading the file: {e}")

def check_selected_essid_in_file(ssid, file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if ssid in line:
                    ssid = line.split('ssid = "')[1].split('"')[0]
                    password = line.split('password = "')[1].split('"')[0]
                    print(f"SSID: {ssid}, Password: {password}")
                    data = password
                    connect_to_wifi(ssid, data)
                    sys.exit()
#                    disconnect_from_wifi()# Disconnect from WiFi when exit button is pressed                
#                    delete_files_in_directory('/etc/NetworkManager/system-connections/')
#                    if connect_to_wifi(ssid, data):
#                        print("Connected successfully!")
#                        sys.exit()
#                    else:
#                        print("Error: Connection activation failed.")
#                        delete_line_in_file(file_path, line)
#                        capture_qr_code()
            else:
                print("No, SSID is not present in the file.")
                capture_qr_code()
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

#def delete_line_in_file(file_path, line_to_delete):
#    try:
#        with open(file_path, 'r') as file:
#            lines = file.readlines()
#        with open(file_path, 'w') as file:
#            for line in lines:
#                if line.strip() != line_to_delete.strip():
#                    file.write(line)
#    except Exception as e:
#        print(f"An error occurred while deleting line from file: {e}")
        
def disconnect_from_wifi():
    try:
        os.system("nmcli device disconnect wlan0")
        print("Disconnected from WiFi")
        play_file.play_audio_file("hearsight_app_disconnected.mp3")
    except Exception as e:
        print(f"Error disconnecting from WiFi: {e}")
#        return None
        sys.exit()

def delete_files_in_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        print("All files deleted successfully.")
        sys.exit()
    except Exception as e:
        print(f"Error: {e}")
#        return None
        sys.exit()

def main():
    global essids

    try:
        interface = find_wireless_interface()

        if interface:
            try:
                result = os.popen(f'iwlist {interface} scan | grep ESSID').read()
                essids = extract_essids(result)
                print(f"Number of available WiFi networks: {len(essids)}")
                print("ESSIDs:", essids)
            except Exception as scan_error:
                print(f"Error during WiFi network scanning: {scan_error}")
                play_file.play_audio_file("no_WiFi_networks_found_enable_mobile_hotspot_and_try_again.mp3")
                time.sleep(0.3)
                sys.exit()
        else:
            print("Wireless interface not found.")
            play_file.play_audio_file("no_WiFi_networks_found_enable_mobile_hotspot_and_try_again.mp3")
            time.sleep(0.3)
            sys.exit()

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

if __name__ == "__main__":
    main()

    if not essids:
        play_file.play_audio_file("no_WiFi_networks_found_enable_mobile_hotspot_and_try_again.mp3")
        time.sleep(1)
        sys.exit()
    else:
        play_file.play_audio_file("press your feature button now.mp3")
        limit = len(essids)
        count = -1

        while True:
            time.sleep(0.0001)
            forward = GPIO.input(450)  # Forward button
            backward = GPIO.input(421)  # Backward button

            if forward:
                count = (count + 1) % limit
                print(count)
            if backward:
                count = (count - 1) % limit
                print(count)

            if forward or backward:
                selected_essid = essids[count]
                print(f"Selected WiFi network: {selected_essid}")
                engine.say(selected_essid)
                engine.runAndWait()

            input_state = GPIO.input(447)  # Feature button
            if input_state == True:
                play_file.play_audio_file("feature_confirmed.mp3")
                ssid = selected_essid
#                check_selected_essid_in_file(ssid)
                check_selected_essid_in_file(ssid, file_path)