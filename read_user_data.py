import pandas as pd
import os
from glob import glob
import cv2
import yaml
from colorama import Fore, Style

# read user data must read literally everything: from the list of specs, consumption profile, to calib images, to the sky photo
# it should save everything about the files so that it can keep track whether changes have been applied
def read_user_data():
    # 4 means that nothing will be executed
    # 3 means that the state of charge estimation will be recalculated
    # 2 means that shading will be recalculated
    # 1 means that raw irradiance will be recalculated
    # 0 means that calibration will be redone
    control_option = 4
    #################################### we first read the Consumption_Profile.xlsx ##########################################
    # read Consumption_Profile.xlsx and check whether the file exist
    print(f"{Fore.YELLOW}Reading your consumption profile sheet...{Style.RESET_ALL}")
    while (1):
        try:
            raw_consumption_profile = pd.read_excel('./SystemData/Consumption_Profile.xlsx', index_col='Hour of day')
            break
        except:
            print(
                f"{Fore.LIGHTRED_EX}Bro... why did u remove Consumption_Profile.xlsx in SystemData, the file is kinda important!{Style.RESET_ALL}")
            input(
                f"{Fore.LIGHTCYAN_EX}Please put the file back and press ENTER to continue, or just close the program and return when you put it back{Style.RESET_ALL}")

    print(f"{Fore.GREEN}Done!{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}Reading saved consumption profile sheet...{Style.RESET_ALL}")

    # read the Save_Consumption_Profile.xlsx and compare the data extracted from this file to Consumption_Profile.
    # if the data is exactly the same,
    try:
        saved_consumption_profile = pd.read_excel('./DebugData/Saved_Consumption_Profile.xlsx', index_col='Hour of day')
        if (saved_consumption_profile.equals(raw_consumption_profile)):
            print(f"{Fore.GREEN}No changes to consumption profile.{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTRED_EX}Some changes to consumption profile detected!{Style.RESET_ALL}")
            raw_consumption_profile.to_excel('./DebugData/Saved_Consumption_Profile.xlsx')
            if control_option > 3:
                control_option = 3

    except:
        print(f'{Fore.LIGHTRED_EX}Welp didnt have Saved_Consumption_Profile.xlsx...{Style.RESET_ALL}')
        raw_consumption_profile.to_excel('./DebugData/Saved_Consumption_Profile.xlsx')

    #################################### first read up System_Specifications.xlsx ######################################
    list_of_specs = ['Lattitude (°)', 'Longitude (°)', 'Elevation (m)', \
                     'Image orientation (°)', 'Image inclination (°)', 'Plane orientation (°)', "Plane inclination (°)", \
                     'Calib vertex short', 'Calib vertex long', 'Calib square size (mm)', \
                     'Start year', 'End year', \
                     'Solar panel peak wattage (W)', 'Converter efficiency (%)', 'Converter max power (W)', \
                     'Charge efficiency (%)', 'Discharge efficiency (%)', 'Max SOC (%)', 'Min SOC (%)', \
                     'Batt nominal capacity (Ah)', 'Batt nominal voltage (V)']

    print(f"{Fore.YELLOW}Reading your specification sheet...{Style.RESET_ALL}")
    while (1):
        try:
            user_data = pd.read_excel('./SystemData/System_Specifications.xlsx', index_col=None)
            break
        except:
            print(f"{Fore.LIGHTRED_EX}Bro... why did u remove System_Specifications.xlsx in SystemData, the file is kinda important!{Style.RESET_ALL}")
            input(f"{Fore.LIGHTCYAN_EX}Please put the file back and press ENTER to continue, or just close the program and return when you put it back{Style.RESET_ALL}")

    print(f"{Fore.GREEN}Done!{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}Reading saved specification sheet...{Style.RESET_ALL}")

    try:
        saved_user_data = pd.read_excel('./DebugData/Saved_System_Specifications.xlsx', index_col=None)

        for i in range(len(list_of_specs)):
            if float(user_data[list_of_specs[i]][0]) == float(saved_user_data[list_of_specs[i]][0]):
                print(f"{Fore.GREEN}No change to " + list_of_specs[i] + f" parameter{Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTRED_EX}Change to " + list_of_specs[i] + " parameter detected! (" + str(saved_user_data[list_of_specs[i]][0]) + " -> " + str(user_data[list_of_specs[i]][0]) + f"){Style.RESET_ALL}")
                user_data.to_excel('./DebugData/Saved_System_Specifications.xlsx')
                if i < 3:
                    if control_option > 0:
                        control_option = 0
                elif i < 10:
                    if control_option > 1:
                        control_option = 1
                else:
                    if control_option > 3:
                        control_option = 3

    except:
        print(f'{Fore.LIGHTRED_EX}Welp didnt have Saved_System_Specifications.xlsx...{Style.RESET_ALL}')
        user_data.to_excel('./DebugData/Saved_System_Specifications.xlsx')

    # before proceeding with opening the sky image and calib images, we should test whether there were any changes made to these directories
    # to protect against forgetting to put the image files in
    while (1): # this outer loop is to check for whether the size of the image is consistent
        print(f"{Fore.YELLOW}Reading sky image and calibration images...{Style.RESET_ALL}")
        while (1): # these inner loops are to check whether the content of the folder are ok
            sky_files = glob('./SkyImageOfSite/*.jpg')
            if len(sky_files) == 0:
                print(f"{Fore.LIGHTRED_EX}Uhmm... did u forgot to put in ANY sky image at all?{Style.RESET_ALL}")
                input(f"{Fore.LIGHTRED_EX}Please put the Black and White sky image into SkyImageOfSite and press ENTER to continue... {Style.RESET_ALL}")
            elif len(sky_files) > 1:
                print(f"{Fore.LIGHTYELLOW_EX}Hmm... you put more than ONE sky image in SkyImageOfSite!{Style.RESET_ALL}")
                input(f"{Fore.LIGHTYELLOW_EX}Please leave only the file you want to use and press ENTER to continue... {Style.RESET_ALL}")
            else:
                break

        # now open the sky image file and start checking if all the calib images share the size of this image
        image_to_convert = cv2.imread(sky_files[0], cv2.IMREAD_GRAYSCALE)
        im_height, im_width = image_to_convert.shape

        # to protect against forgetting putting the calib files in or warns about insufficient calib set
        while (1): # these inner loops are to check whether the content of the folder are ok
            calib_files = glob('./CalibrationImages/*.jpg')
            if len(calib_files) == 0:
                print(f"{Fore.LIGHTRED_EX}Uhmm... did u forgot to put in ANY calibration images at all?{Style.RESET_ALL}")
                input(f"{Fore.LIGHTRED_EX}Please put the calibration images into CalibrationImages and press ENTER to continue... {Style.RESET_ALL}")
            elif len(calib_files) <= 8:
                print(f"{Fore.LIGHTYELLOW_EX}Hmm... that is not a lot of calibration images, maybe insufficient for a good calibration{Style.RESET_ALL}")
                input(f"{Fore.LIGHTYELLOW_EX}Well you should consider adding more calib images if the result turns out bad. But for now you can press ENTER to continue... {Style.RESET_ALL}")
                break
            else:
                break

        calib_dim_ok = 1
        for fnames in calib_files:
            calib_image = cv2.imread(fnames, cv2.IMREAD_GRAYSCALE)
            calib_im_height, calib_im_width = calib_image.shape
            if (calib_im_height != im_height or calib_im_width != im_width):
                print(f'{Fore.LIGHTRED_EX}Detected inconsistent size between sky photo and calib images!{Style.RESET_ALL}')
                print(f'{Fore.LIGHTRED_EX}Sky photo is ' + str(im_height) + ' by ' + str(
                    im_width) + ' while ' + fnames + ' is ' + str(calib_im_height) + ' by ' + str(
                    calib_im_width) + f'{Style.RESET_ALL}')
                input(f'{Fore.LIGHTRED_EX}Please fix this problem and press ENTER to continue... {Style.RESET_ALL}')
                calib_dim_ok = 0
                break
        if calib_dim_ok:
            break

    # with sky files and calib files loaded up, its time to check whether there were any changes
    # now we should read up and check their recent modification time
    try:
        with open('imagestatus.yml') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
            stored_sky_image_metadata = data['sky_image_metadata']
            stored_calib_images_metadata = data['calib_images_metadata']

            sky_image_metadata = list(os.stat(sky_files[0]))
            calib_images_metadata = [list(os.stat(calib_fnames)) for calib_fnames in calib_files]

            # well we would not want to care about the last access time
            sky_image_metadata[7] = 0
            for i in range(len(calib_images_metadata)):
                calib_images_metadata[i][7] = 0

            if (stored_sky_image_metadata == sky_image_metadata):
                print(f"{Fore.GREEN}No changes in SkyImageOfSite detected.{Style.RESET_ALL}")
            else:
                if (control_option > 2):
                    control_option = 2
                print(f"{Fore.LIGHTRED_EX}Changes in SkyImageOfSite detected!{Style.RESET_ALL}")

            if (stored_calib_images_metadata == calib_images_metadata):
                print(f"{Fore.GREEN}No changes in CalibrationImages detected.{Style.RESET_ALL}")
            else:
                if (control_option > 0):
                    control_option = 0
                print(f"{Fore.LIGHTRED_EX}Changes in CalibrationImages detected!{Style.RESET_ALL}")
            f.close()

        # write down the new sky image metadata and calib images metadata
        with open('imagestatus.yml','w') as f:
            metadata = {'sky_image_metadata': sky_image_metadata, 'calib_images_metadata' : calib_images_metadata}
            yaml.dump(metadata, f, Dumper=yaml.SafeDumper)
            f.close()

    except EnvironmentError:
        control_option = 0      # force control_option = 0 because no metadata stored on calib... meaning we are forced to redo the calib once
        print(f'{Fore.LIGHTRED_EX}Welp didnt have metadata stored...{Style.RESET_ALL}')
        with open('imagestatus.yml','w') as f:
            sky_image_metadata = list(os.stat(sky_files[0]))[8]
            calib_images_metadata = [list(os.stat(calib_fnames))[8] for calib_fnames in calib_files]

            metadata = {'sky_image_metadata': sky_image_metadata, 'calib_images_metadata' : calib_images_metadata}
            yaml.dump(metadata, f, Dumper=yaml.SafeDumper)
            f.close()

# returns the 4 main pieces of information: the system data, the consumption profile, the
    return user_data, raw_consumption_profile, calib_files, image_to_convert, control_option


