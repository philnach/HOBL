PLE Network installs for SBCT images.
For details see Readme under UPDATES folders.

--- USAGE:
SetupODE.CMD to install images from \\PLEWUSRV1\PLEGolden - will find latest released image.
OR -> Run SetupODE and pass params as needed when using custom image location

        [string] $BuildLink= $null,
        [string] $WiFi_Install = $true | $false

WiFi install True -> Copy image to local partiton - Wipes Windows and WinRE
WiFi Install False -> Boot WinPE and install image over USB NET - Wipes disk


------------ CHANGES ---------------------------------

2.4 - Updates for Glissade SBCT wim name changes

2.3 - Minor GLISSADE Updates
      1st support for use outside of WTT/HLK Clients
      WIFI fixes for GLISSADE

2.0 - Added support for GLISSADE IMAGE type
      WiFi install support

OWNER: Dwight Carver


