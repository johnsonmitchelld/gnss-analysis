from ftplib import FTP_TLS
ftps = ftps = FTP_TLS('gdc.cddis.eosdis.nasa.gov')
ftps.login()
ftps.prot_p()
print(ftps.nlst())