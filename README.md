# gps-station 

gps-station is a project that is essentially a TCP server, its purpose is to let GPS devices with various protocols connect to it, process their data and send them to backend for storage and further processing.

## Supported Protocols
- H02


## Devices that gps-station works with
- ST-901 (SinoTrack)
> _**NOTE**_: those are devices that **`gps-station`** has been tested on, ideally it should work on every device that uses any one of the protocols listed in **Supported Protocols** section. If you know for a fact that it works with a particular device and it is not listed here, please make a pull request with updated device list.


## How to run
To run **`gps-station`** you need:
- Docker installed and running
- To be in the directory of this package

1. Build **`gps-station`** image: `docker build -t gps_station .`
2. Run the built image: `docker run --name gps_station -p 8090:8090/tcp --mount type=bind,source=$(pwd)/logs/,destination=/gps-station/logs/ --env BACKEND_URL=http://localhost:8000/add-location/ gps_station`
3. Make sure port `8090` is open (I use [this tool](https://www.yougetsignal.com/tools/open-ports/))

> _**NOTE**_: don't forget to replace `BACKEND_URL` environment variable value in step 2 with your own.

