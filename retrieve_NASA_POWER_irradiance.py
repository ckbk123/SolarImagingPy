
import os, json, requests
import numpy as np
import pandas as pd
from colorama import Fore, Style

# lat and long are coordinates in float
# start_time and end_time has to be given as YYYYMMDD
def retrieve_NASA_POWER_irradiance(lat, long, start_time, end_time):
    # note that ALLSKY_SFC_SW_DIFF is diffuse sky while ALLSKY_SFC_SW_DWN is diffuse + direct
    base_url = r"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=ALLSKY_SFC_SW_DIFF,ALLSKY_SFC_SW_DNI&community=RE&longitude={longitude}&latitude={latitude}&start={start_time}&end={end_time}&format=JSON&time-standard=UTC"

    api_request_url = base_url.format(longitude=long, latitude=lat, start_time=start_time, end_time=end_time)
    print(api_request_url)

    response = requests.get(url=api_request_url, verify=True, timeout=30.00)

    content = json.loads(response.content.decode('utf-8'))

    records = content['properties']['parameter']

    df = pd.DataFrame.from_dict(records)

    # these are to make the NASA power output somewhat consistent with PVGIS data
    # but we are going to need to solar position throughout the period...
    datetime_index = pd.to_datetime(df.index, format="%Y%m%d%H")
    direct_data = df['ALLSKY_SFC_SW_DNI']
    diffuse_data = df['ALLSKY_SFC_SW_DIFF']

    return direct_data.to_numpy(), diffuse_data.to_numpy(), datetime_index

