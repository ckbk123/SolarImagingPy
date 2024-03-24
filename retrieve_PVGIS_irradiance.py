
import pvlib.iotools.pvgis as PVGIS
from colorama import Fore, Style

def retrieve_PVGIS_irradiance(lat, long, start_year, end_year, inclination, orientation):
    print(f'{Fore.YELLOW}Fetching hourly irradiation from PVGIS...{Style.RESET_ALL}')
    data, meta, inputs = PVGIS.get_pvgis_hourly(latitude=lat, longitude=long, start=start_year, end=end_year,
                                                outputformat='json', components=True, usehorizon=False,
                                                surface_tilt=inclination, surface_azimuth=180+orientation)
    print(f'{Fore.GREEN}Done!{Style.RESET_ALL}')
    # return the direct irradiance, diffuse irradiance, and time (most likely in panda datetime format, ambiguous documentation)
    return data['poa_direct'], data['poa_sky_diffuse'], data.index