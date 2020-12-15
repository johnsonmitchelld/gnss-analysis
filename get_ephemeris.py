from ftplib import FTP_TLS
import gzip
import shutil
ftps = ftps = FTP_TLS('gdc.cddis.eosdis.nasa.gov')
ftps.login()
ftps.prot_p()
print(ftps.nlst('gnss/data/daily/2020/brdc'))
filename = 'BRDC00IGS_R_20200010000_01D_MN.rnx.gz'
with open(filename, 'wb') as handle:
    ftps.retrbinary('RETR gnss/data/daily/2020/brdc/BRDC00IGS_R_20200010000_01D_MN.rnx.gz', handle.write)

with gzip.open('BRDC00IGS_R_20200010000_01D_MN.rnx.gz', 'rb') as f_in:
    with open('BRDC00IGS_R_20200010000_01D_MN.rnx', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)