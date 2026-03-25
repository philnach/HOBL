# Change settings of the host computer's camera, intended to be a USB-attached web cam

import argparse
import cv2
import time
# from PIL import Image
 
 
def configure_camera_settings(camera, focus, exposure):
    # We are using a locally attached USB camera
    cap = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
 
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    result = cap.set(cv2.CAP_PROP_FOCUS, focus)
    if not result:
        print("ERROR: Unable to set focus to specified value.  It needs to be in increments of 5.  Or camera may be disconnected.")
    else:
        f = cap.get(cv2.CAP_PROP_FOCUS)
        print("Set focus to: " + str(f))
 
    time.sleep(2)
    result_exposure = cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    if not result_exposure:
        print("ERROR: Unable to set exposure.")
    else:
        e = cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f"Set exposure to: " + str(e))
 
    # result_brightness = cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
    # if not result_brightness:
    #     print("ERROR: Unable to set brightness.")
    # else:
    #     b = cap.get(cv2.CAP_PROP_BRIGHTNESS)
    #     print(f"Set brightness to: " + str(b))
 
    # result_contrast = cap.set(cv2.CAP_PROP_CONTRAST, contrast)
    # if not result_contrast:
    #     print("ERROR: Unable to set contrast.")
    # else:
    #     c = cap.get(cv2.CAP_PROP_CONTRAST)
    #     print(f"Set contrast to: " + str(c))
   
    cap.release()
    # cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Disables autofocus on attached USB camera.')
    parser.add_argument('-camera', nargs='?', default=0, help="The camera ID number")
    parser.add_argument('-focus', nargs='?', default=25, help="Focus value in increments of 5")
    parser.add_argument('-exposure', nargs='?', default=-5, help="Exposure value")
    parser.add_argument('-brightness', nargs='?', default=128, help="Brightness value")
    parser.add_argument('-contrast', nargs='?', default=128, help="Contrast value")
    args = parser.parse_args()
 
    configure_camera_settings(int(args.camera), int(args.focus), int(args.exposure))