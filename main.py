# This is a sample Python script.
from colorama import Fore, Style
from read_user_data import read_user_data
from compute_diffuse_shading_factor import compute_diffuse_shading_factor
from compute_direct_shading_factor import compute_direct_shading_factor
from import_camera_intrinsic_function import import_camera_intrinsic_function
from retrieve_PVGIS_irradiance import retrieve_PVGIS_irradiance
from retrieve_NASA_POWER_irradiance import retrieve_NASA_POWER_irradiance, adjust_NASA_irradiance_with_surface_position
from sunpath_from_astropy import sunpath_from_astropy
from calibrate_camera import calibrate_camera

import pandas as pd

import numpy as np
from state_of_charge_estimation import state_of_charge_estimation
import matplotlib.backends.backend_tkagg
import matplotlib.backends.backend_pdf
matplotlib.use('TkAgg')

if __name__ == '__main__':
    print(f"{Fore.LIGHTBLUE_EX}Welcome to CKBK's shading estimation tool{Style.RESET_ALL}")

    print(f"{Fore.LIGHTMAGENTA_EX}Remind you all the relevant information: calibration images to be put in CalibrationImages, ONE black and white sky photo in SkyImageOfSite, the system's consumption in SystemData/Consumption_Profile.xlsx, the system's specs in System_Specifications.xlsx...{Style.RESET_ALL}")

    while (1):
        user_data, raw_consumption_profile, calib_files, skyimage, control_sequence = read_user_data()
        temp = input(f"{Fore.LIGHTCYAN_EX}Press ENTER to initiate an estimation...{Style.RESET_ALL}")

        # this is no change, so ask the user if they want to redo everything from scratch
        # this usually could fix some bugs
        if (control_sequence == 4):
            print(f"{Fore.LIGHTCYAN_EX}It seems there are no changes available. Type r then ENTER to redo everything from scratch. Otherwise, type anything then ENTER and the procedure is skipped.{Style.RESET_ALL}")
            answer = input(f"{Fore.LIGHTCYAN_EX}Your choice... {Style.RESET_ALL}")
            if (answer == 'r'):
                control_sequence = 1

        ############################################# CALIBRATE CAMERA #################################################
        if (control_sequence < 1):
            calibrate_camera(int(user_data['Calib vertex short'][0]), int(user_data['Calib vertex long'][0]),
                             float(user_data['Calib square size (mm)'][0]), calib_files)

        ##################################### RAW IRRADIANCE + SOLAR COORDS ############################################
        if (control_sequence < 2):
            hor_direct_irradiance, hor_diffuse_irradiance, time_array = retrieve_NASA_POWER_irradiance(
                float(user_data['Lattitude (°)'][0]),
                float(user_data['Longitude (°)'][0]),
                str(int(user_data['Start year'][0])),
                str(int(user_data['End year'][0])))
            astropy_coords = sunpath_from_astropy(
                float(user_data['Longitude (°)'][0]),
                float(user_data['Lattitude (°)'][0]),
                float(user_data['Elevation (m)'][0]) ,
                time_array)
            direct_irradiance, diffuse_irradiance = adjust_NASA_irradiance_with_surface_position(
                hor_direct_irradiance,
                hor_diffuse_irradiance,
                astropy_coords[0],
                astropy_coords[1],
                0,0)
                # float(user_data['Orientation (°)'][0]),
                # float(user_data['Inclination (°)'][0]))

            raw_irradiance_data = {'Raw_direct': direct_irradiance, 'Raw_diffuse': diffuse_irradiance, 'Solar_az': astropy_coords[0], 'Solar_zen': astropy_coords[1]}
            raw_irradiance_dataframe = pd.DataFrame(raw_irradiance_data, index=time_array)
            raw_irradiance_dataframe.index.name = 'Timeseries'
            raw_irradiance_dataframe.to_csv('./DebugData/raw_irradiance.csv')

        ################################## COMPENSATE IRRADIANCE WITH SHADING ##########################################
        if (control_sequence < 3):
            raw_irradiance_data = pd.read_csv('./DebugData/raw_irradiance.csv', index_col = 'Timeseries')
            time_array = pd.to_datetime(raw_irradiance_data.index)
            direct_irradiance = raw_irradiance_data['Raw_direct'].tolist()
            diffuse_irradiance = raw_irradiance_data['Raw_diffuse'].tolist()

            solar_az = raw_irradiance_data['Solar_az']
            solar_zen = raw_irradiance_data['Solar_zen']
            astropy_coords = [np.array(solar_az), np.array(solar_zen)]

            poly_incident_angle_to_radius, principal_point, estimated_fov = import_camera_intrinsic_function()
            im_height, im_width = skyimage.shape

            diffuse_shading_factor = compute_diffuse_shading_factor(
                skyimage,
                poly_incident_angle_to_radius,
                principal_point,
                estimated_fov,
                im_height,
                im_width)

            direct_shading_factor = compute_direct_shading_factor(
                skyimage,
                im_height,
                im_width,
                poly_incident_angle_to_radius,
                principal_point,
                float(user_data['Orientation (°)'][0]),
                float(user_data['Inclination (°)'][0]),
                estimated_fov,
                astropy_coords,
                time_array)

            compensated_direct = np.multiply(np.array(direct_irradiance), np.array(1-direct_shading_factor))
            compensated_diffuse = np.array(diffuse_irradiance) * (1-diffuse_shading_factor)
            final_irradiance = compensated_direct + compensated_diffuse

            compensated_irradiance_data = {'Compensated_direct': compensated_direct, 'Compensated_diffuse': compensated_diffuse}
            compensated_irradiance_dataframe = pd.DataFrame(compensated_irradiance_data, index=time_array)
            compensated_irradiance_dataframe.index.name = 'Timeseries'
            compensated_irradiance_dataframe.to_csv('./DebugData/compensated_irradiance.csv')

        ######################################## ESTIMATE THE SYSTEM SOC ###############################################
        if (control_sequence < 4):
            compensated_irradiance_data = pd.read_csv('./DebugData/compensated_irradiance.csv', index_col = 'Timeseries')
            time_array = pd.to_datetime(compensated_irradiance_data.index)
            final_irradiance = np.array(compensated_irradiance_data['Compensated_direct'].tolist()) + np.array(compensated_irradiance_data['Compensated_diffuse'].tolist())

            state_of_charge_estimation(
                final_irradiance,
                time_array,
                float(user_data['Solar panel peak wattage (W)'][0]),
                float(user_data['Converter efficiency (%)'][0]),
                float(user_data['Converter max power (W)'][0]),
                float(user_data['Charge efficiency (%)'][0]),
                float(user_data['Discharge efficiency (%)'][0]),
                float(user_data['Max SOC (%)'][0]),
                float(user_data['Min SOC (%)'][0]),
                float(user_data['Batt nominal capacity (Ah)'][0]),
                float(user_data['Batt nominal voltage (V)'][0]))

        print(f"{Fore.LIGHTCYAN_EX}So... u good with the result? If not, you can modify the information and we'll do another estimation.{Style.RESET_ALL}")
        user_input = 'a'
        while user_input != 'e' and user_input != 'c':
            import time, sys
            user_input = input(f'{Fore.LIGHTRED_EX}Type e then ENTER to exit the program, type c then ENTER to relaunch an estimation: {Style.RESET_ALL}')
            if (user_input == 'e'):
                print(f"{Fore.LIGHTBLUE_EX}Thank you for using CKBK's shading estimation tool. Hope you have a lovely day!{Style.RESET_ALL}")
                time.sleep(1)
                sys.exit()
            elif (user_input == 'c'):
                print(f"{Fore.LIGHTBLUE_EX}The program will now check for what you modified and re-run only the necessary sections...{Style.RESET_ALL}")
                time.sleep(1)


