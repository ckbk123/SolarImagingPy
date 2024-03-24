import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
from colorama import Fore, Style
import pandas as pd

# this function just gets the solar azimuth + zenith (in rad) over time. Reference frame described in the function below
def sunpath_from_astropy(longitude, latitude, ground_level, time_array):
    print(f'{Fore.YELLOW}Finding solar trajectory throughout the estimation period using AstroPy...{Style.RESET_ALL}')

    astropy_time = Time(time_array)
    deployment_location = coord.EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=ground_level * u.m)

    frame_prediction = coord.AltAz(obstime=astropy_time, location=deployment_location)

    sun_pos_array = coord.get_sun(astropy_time).transform_to(frame_prediction)

    # We have a problem here: this Az/Zenith info is like... random af in terms of coordinates
    # Zenith has no problem: its the angle between sun and line perpendicular to the ground toward the sky
    # Azimuth has problem: vector toward North is 0 and clockwise North-East-South-West is the direction
    # If you check with the Oxyz coords, this doesnt add up
    # Therefore, we have to convert it over to image coords where Ox points toward West, Oy toward South, Oz toward sky
    # but no worries the extrinsic function took care of this
    zen_array = (sun_pos_array.zen).value
    az_array = (sun_pos_array.az).value

    data = {'Timeseries': time_array, 'Zen_array': zen_array, 'Az_array': az_array}
    dataframe = pd.DataFrame(data)
    dataframe.set_index('Timeseries')
    dataframe.to_csv('./DebugData/solar_coords.csv')

    print(f'{Fore.GREEN}Done!{Style.RESET_ALL}')

    return [az_array, zen_array]