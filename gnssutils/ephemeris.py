from ftplib import FTP_TLS, FTP
import ftplib
import gzip
import shutil
import os
from datetime import datetime, timedelta, timezone
import georinex as gr
import xarray
import unlzw3
import pandas as pd

# https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/gnss_mgex.html
# https://igs.org/mgex/data-products/#data
# merged daily ephemerides: gnss/data/daily/2020/brdc/
# ftp://igs.bkg.bund.de/IGS/BRDC/2020/366/
# https://igs.bkg.bund.de/dataandproducts/overviewindex
# ftp://igs.bkg.bund.de/IGS/


class EphemerisManager():
    def __init__(self, data_directory = os.path.join(os.getcwd(), 'data', 'ephemeris')):
        self.data_directory = data_directory
        self.data = None
        self.leapseconds = None
        self.downloadtime = None
        
    def get_ephemeris(self, timestamp, satellites=None):
        systems = EphemerisManager.get_constellations(satellites)
        if not isinstance(self.data, pd.DataFrame):
            self.load_data(timestamp)
        data = self.data
        if satellites:
            data = data.loc[data['sv'].isin(satellites)]
        data = data.loc[data['time'] < timestamp]
        data = data.sort_values('time').groupby('sv').last()
        data['Leap Seconds'] = self.leapseconds
        return data

    def load_data(self, timestamp):
        timetuple = timestamp.timetuple()
        extension = EphemerisManager.get_filetype(timestamp)
        directory = 'gnss/data/hourly/' + \
            str(timetuple.tm_year) + '/' + str(timetuple.tm_yday).zfill(3)
        filename = 'hour' + str(timetuple.tm_yday).zfill(3) + \
            '0.' + str(timetuple.tm_year)[-2:] + 'g' + extension
        data_list = []
        data = self.get_ephemeris_dataframe(
            'gdc.cddis.eosdis.nasa.gov', directory, filename, secure=True)
        filename = 'hour' + str(timetuple.tm_yday).zfill(3) + \
            '0.' + str(timetuple.tm_year)[-2:] + 'n' + extension
        data_list.append(data)
        data = self.get_ephemeris_dataframe(
            'gdc.cddis.eosdis.nasa.gov', directory, filename, secure=True)
        data_list.append(data)
        directory = 'gnss/data/daily/' + str(timetuple.tm_year) + '/brdc'
        filename = 'BRDC00IGS_R_' + \
            str(timetuple.tm_year) + \
            str(timetuple.tm_yday).zfill(3) + '0000_01D_MN.rnx.gz'
        data = self.get_ephemeris_dataframe(
            'gdc.cddis.eosdis.nasa.gov', directory, filename, secure=True)
        data_list.append(data)
        filename = 'brdc' + str(timetuple.tm_yday).zfill(3) + \
            '0.' + str(timetuple.tm_year)[-2:] + 'n' + extension
        data = self.get_ephemeris_dataframe(
            'gdc.cddis.eosdis.nasa.gov', directory, filename, secure=True)
        data_list.append(data)
        filename = 'brdc' + str(timetuple.tm_yday).zfill(3) + \
            '0.' + str(timetuple.tm_year)[-2:] + 'g' + extension
        data = self.get_ephemeris_dataframe(
            'gdc.cddis.eosdis.nasa.gov', directory, filename, secure=True)
        data_list.append(data)
        directory = '/IGS/BRDC/' + \
            str(timetuple.tm_year) + '/' + str(timetuple.tm_yday).zfill(3)
        filename = 'BRDC00WRD_S_' + \
            str(timetuple.tm_year) + \
            str(timetuple.tm_yday).zfill(3) + '0000_01D_MN.rnx.gz'
        data = self.get_ephemeris_dataframe(
            'igs.bkg.bund.de', directory, filename, secure=False)
        data_list.append(data)
        filename = 'brdc' + str(timetuple.tm_yday).zfill(3) + \
            '0.' + str(timetuple.tm_year)[-2:] + 'n' + extension
        data = self.get_ephemeris_dataframe(
            'igs.bkg.bund.de', directory, filename, secure=False)
        data_list.append(data)
        filename = 'brdc' + str(timetuple.tm_yday).zfill(3) + \
            '0.' + str(timetuple.tm_year)[-2:] + 'g' + extension
        data = self.get_ephemeris_dataframe(
            'igs.bkg.bund.de', directory, filename, secure=False)
        data = data.append(data_list, ignore_index=True)
        data.reset_index(inplace=True)
        
        self.data = data

    @staticmethod
    def get_filetype(timestamp):
        # IGS switched from .Z to .gz compression format on December 1st, 2020
        if timestamp >= datetime(2020, 12, 1, 0, 0, 0, tzinfo=timezone.utc):
            extension = '.gz'
        else:
            extension = '.Z'
        return extension

    @staticmethod
    def get_leapseconds(filename):
        with open(filename) as f:
            for line in f:
                if 'LEAP SECONDS' in line:
                    return int(line.split()[0])
                if 'END OF HEADER' in line:
                    return None
                
    @staticmethod
    def get_constellations(satellites):
        if type(satellites) is list:
            systems = set()
            for sat in satellites:
                systems.add(sat[0])
            return list(systems)
        else:
            return None

    def get_ephemeris_dataframe(self, url, directory, filename, secure=False, constellations = None):
        if url == 'igs.bkg.bund.de':
            dest_filepath = os.path.join(self.data_directory, 'igs', filename)
        else:
            dest_filepath = os.path.join(self.data_directory, 'nasa', filename)
        decompressed_filename = os.path.splitext(dest_filepath)[0]
        if not os.path.isfile(decompressed_filename):
            try:
                self.get_file(url, directory, filename, dest_filepath, secure)
                self.decompress_file(dest_filepath)
            except ftplib.error_perm as err:
                return pd.DataFrame()
        if not self.leapseconds:
            self.leapseconds = EphemerisManager.get_leapseconds(decompressed_filename)
        if constellations:
            data = gr.load(decompressed_filename, use=constellations).to_dataframe()
        else:
            data = gr.load(decompressed_filename).to_dataframe()
        data.dropna(how='all', inplace=True)
        data.reset_index(inplace=True)
        data['source'] = decompressed_filename
        data['time'] = data['time'].dt.tz_localize('UTC')
        return data

    def get_file(self, url, directory, filename, dest_filepath, secure=False):
        ftp = self.connect(url, secure)
        src_filepath = directory + '/' + filename
        try:
            with open(dest_filepath, 'wb') as handle:
                ftp.retrbinary(
                    'RETR ' + src_filepath, handle.write)
        except ftplib.error_perm as err:
            print('Attempted to retrieve ' + src_filepath + ' from ' + url)
            print(err)
            os.remove(dest_filepath)
            raise ftplib.error_perm

    def decompress_file(self, filepath):
        extension = os.path.splitext(filepath)[1]
        if extension == '.gz':
            with gzip.open(filepath, 'rb') as f_in:
                with open(filepath[:-3], 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif extension == '.Z':
            with open(filepath, 'rb') as f_in:
                with open(filepath[:-2], 'wb') as f_out:
                    f_out.write(unlzw3.unlzw(f_in.read()))
        os.remove(filepath)

    def connect(self, url, secure):
        if secure:
            ftp = FTP_TLS(url)
            ftp.login()
            ftp.prot_p()
        else:
            ftp = FTP(url)
            ftp.login()
        return ftp

    def listdir(self, url, directory, secure):
        ftp = self.connect(url, secure)
        dirlist = ftp.nlst(directory)
        dirlist = [x for x in dirlist]
        print(dirlist)


if __name__ == '__main__':
    repo = EphemerisManager()
    target_time = datetime.utcnow()
    target_time = datetime(2021,1, 5, 12, 0, 0, tzinfo = timezone.utc)
    data = repo.get_ephemeris(target_time)