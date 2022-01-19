# mlops-pipeline
Machine Learning Ops pipeline 

## About the projet

## Prerequisites
Please ensure the following software are already installed on your machine.
* MongoDB Community Edition 5.0 [link](http://www.google.fr/)

## Installation
  1. Clone the repository
  
    git clone https://github.com/narrahmane/mlops-pipeline.git
    cd mlops-pipeline
    
  2. Initialize environment variables
    
    source ./init.sh
    
  3. Create conda environment from requirements.txt
    
    conda create --name <env> --file requirements.txt
    conda activate <env>
    pip install rdkit-pypi==2021.9.4 

## Launch Mongo DB server
    
    brew services start mongodb-community


## Launch Web App server

    python app.py

## Usage

### Ingest and Transform

    python pipeline.py --steps=INGEST+TRANSFORM

### Train and Deploy

    python pipeline.py --steps=TRAIN+DEPLOY

### Use endpoints


  1. /
    
    curl -X GET "http://localhost:${EXSCIENTIA_ASSESMENT_WEBAPP_SERVER_PORT}/
  
  2. /compound?id=<COMPOUND_ID>
  
    curl -X GET "http://localhost:${EXSCIENTIA_ASSESMENT_WEBAPP_SERVER_PORT}/compound?id=1117973"   
  
  2. /bestmodel
  
    curl -X GET "http://localhost:4049/bestmodel?objectiveId=OBJ-1234"
  
  3. /predict?molecular_weight=<COMPOUND_MOLECULAR_WEIGHT>
  
    curl -X GET "http://localhost:${EXSCIENTIA_ASSESMENT_WEBAPP_SERVER_PORT}/predict?molecular_weight=4638.9930"
  
  

## Kill Mongo DB server

    mongo exscientia --host $EXSCIENTIA_ASSESMENT_DB_URL --port $EXSCIENTIA_ASSESMENT_DB_PORT --eval "db.dropDatabase()"
    brew services stop mongodb-community
