import cv2
import os
from colorama import Fore, Style

# it checks for any image file placed in SkyImageOfSite directory
# if there are multiple files in SkyImageOfSite, it will take the first one and tell the user which one it uses
def read_image_file(control_sequence):
    print(f"{Fore.YELLOW}Reading your sky image...")

    if control_sequence < 1:
        print(f"{Fore.LIGHTRED_EX}IMPORTANT REMINDER: {Fore.LIGHTCYAN_EX}the image must be in black and white!! Script DOES NOT CHECK FOR THIS.{Style.RESET_ALL}")
        input(f"{Fore.LIGHTRED_EX}Are you sure that you put the Black and White version in SkyImageOfSite? (Press ENTER to continue){Style.RESET_ALL}")

    files = os.listdir('./SkyImageOfSite')

    if (len(files) > 1):
        print(f"{Fore.RED}More than one file detected, therefore " + files[0] + f" will be used!{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Detected " + files[0] + f"{Style.RESET_ALL}")

    image_to_convert = cv2.imread("./SkyImageOfSite/"+files[0], cv2.IMREAD_GRAYSCALE)

    im_height, im_width = image_to_convert.shape

    return image_to_convert, im_height, im_width