# CoronaView<sup>TM</sup> by The SIMPsons
This is a visualization of the spread of COVID-19 with data incorporated into an interactable world map, 
providing a broad overview with the ability to obtain more data by clicking on a region.

## Roster
David Lupea: Project Manager  
Joseph Lee: Backend  
Eric Lam: Data Management  
Michael Zhang: Frontend

## Launch Codes
Assumes Python3 and pip are installed.  
Virtual environment recommended.
### Cloning
```shell script
git clone git@github.com:DavidLupea/The-SIMPsons_dlupea00_jlee01_elam00_mzhang00.git
cd The-SIMPsons_dlupea00_jlee01_elam00_mzhang00
```
### Dependencies
```shell script
pip install -r ./requirements.txt
```
### Running
```shell script
python3 ./app/__init__.py
```
Open your browser of choice and go to http://localhost:5000/
### Updating Data
```shell script
python ./app/db_builder.py
```