igs.bkg.bund.de new daily folder appeared at: 00:18 UTC
brdc glonass and gps files from nasa appear around 01:10 UTC
brdc combined updated with ionosphere and leapseconds around 02:00 UTC
looks like optimal strategy is:
if data is from yesterday (UTC) or earlier:
    if all you need is GPS and GLONASS:
        get GPS and GLONASS files from NASA for that day
    else:
        try combined BRDC from nasa
        if that doesn't exist (most likely because it's from too long ago):
            get gps file from NASA (and GLONASS if necessary)
        if it doesn't have leap second and iono data (aka hasn't been post-processed yet):
            get gps file from NASA and combine with NASA combined
if from today UTC:
    get gps file from NASA for ionosphere and leap seconds and combined brdc file from igs for other sat systems
    if too recent, get those same files from yesterday