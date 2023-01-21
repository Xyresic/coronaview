# CoronaView<sup>TM</sup>
This is a visualization of the spread of COVID-19 with data incorporated into an interactable world map, 
providing a broad overview with the ability to obtain more data by clicking on a region.  
[Click here for live demo!](https://coronaviewtm.onrender.com/)  
Data sourced from [Humanitarian Date Exchange](https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases).

## Launch Codes
Assumes Python3 and pip are installed.  
Virtual environment recommended.
### Cloning
```shell script
git clone git@github.com:Xyresic/coronaview.git
cd coronaview
```
### Dependencies
```shell script
pip install -r ./requirements.txt
```
### Running
```shell script
python3 -m app.__init__
```
Open your browser of choice and go to http://localhost:5000/
### Updating Data
```shell script
python3 -m app.db_builder
```
