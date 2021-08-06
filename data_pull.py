import glob
import io
import logging.config
import os
import zipfile
from configparser import ConfigParser
from datetime import datetime

import pandas as pd
import requests

from config import constants as c

# Configuration values
config = ConfigParser()
config.read(c.CONFIG_FILE)

download_folder = config.get('FOLDER', 'DATA')
archive_folder = config.get('FOLDER', 'ARCHIVE')
log_folder = config.get('FOLDER', 'LOG')

nse_url = config.get('NSE', 'URL')
starting_date = config.get('NSE', 'STARTING_DATE')

# Create folder if not exist
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

if not os.path.exists(archive_folder):
    os.makedirs(archive_folder)

if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Initialize log
logging.config.fileConfig(c.LOG_CONFIG_FILE, disable_existing_loggers=False)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info('Started.')


def main():

    # Set start date as max of downloaded file date from archive folder, end date as today
    downloaded_files = glob.glob(f'{archive_folder}/*.csv')
    files = [os.path.basename(d) for d in downloaded_files]
    files_date = [datetime.strptime(f, 'cm%d%b%Ybhav.csv') for f in files]
    start_date = starting_date if not files_date else max(files_date)
    logger.info(f'Starting date for download - {start_date}')

    # Iterate through date range and download

    # start_date, end_date = '1/1/2005', '31/12/2006' # For custom date start, end
    # date_range = pd.bdate_range(start=start_date, end=end_date).tolist() # For custom date range
    date_range = pd.bdate_range(
        start=start_date, end=datetime.today()).tolist()

    for i, date in enumerate(date_range, 1):
        year, month = date.year, date.strftime('%b').upper()
        bhav_file_url = f'''{nse_url}{year}/{month}/cm{date.strftime('%d')}{month}{year}bhav.csv.zip'''

        try:
            r = requests.get(bhav_file_url, timeout=60)
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(download_folder)
                logger.info(
                    f'Out of {len(date_range)} - {i} processed.{bhav_file_url} - Downloaded.')
            else:
                logger.warn(
                    f'Out of {len(date_range)} - {i} processed.{bhav_file_url} - Invalid URL.')
        except:
            logger.warn(
                f'Out of {len(date_range)} - {i} processed.{bhav_file_url} - No Response.')


if __name__ == '__main__':
    main()
