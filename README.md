# mlops-pipeline
Machine Learning Ops pipeline 

## About the projet

The goal of this small project is to build a Machine Learning Pipeline from data ingestion to model deployment.

**We will serve a machine learning model that predicts the compound number of atoms given his molecular weight.**


### Global architecture

![global-architecture](https://user-images.githubusercontent.com/8875161/150154422-79c024c0-6ab9-4c2f-9ddf-211e16520b00.png)


### A - Ingestion
1. Read a compounds.json raw file.
2. It adds the `processed_date` field for each compound.
3. Each compound will be added to a mongodb collection `compound_raw`.
    
### B - Transformation and Enrichment
1.  Read the `compounds_raw` collection
2. Update the `processed_date` field.
3. Add absolute path to `image` field.
4. Enrich the compound with it's atoms number `num_atom`. (We are using rdkit chemical python package.)
5. Push enriched compound to `compounds` collection
 
### C - Training: Linear Regression experiment (~ 0.99 R^2 and 0.89 RMSE)
1. Split train, validation and test set
2. Use `molecular_weight as feature` and `num_atoms as target`
4. Train simple linear regression model using scikit-learn
5. Evaluate model both on train set, validation and test set using [R^2](https://en.wikipedia.org/wiki/Coefficient_of_determination) and [Root Mean Squared Error](https://www.statisticshowto.com/probability-and-statistics/regression-analysis/rmse-root-mean-square-error/) metrics
6. Push experiment object to `experiments` collection. It contains following information about the experiment:
     - model, weights, scores
     - ids of data used in train, val and test set
     - descriptive statistics on the whole set (eg. mean, std, ...)
 
### D - Deployment: Deploy ML model
1. Check if the new experiment is better than the current best model in production. We define better as 'improvements for train, val and test scores'.
2. If new model is best, deploy it by replacing the current model in `models` collection. Business usecase model are determined with `objectiveId` field in experiment.

### E - API
A web app is provided to:
  1. Predict atoms number by providing molecular weight
  2. Get best experiment for objectiveID=OBJ-1234 (Our id business usecase)
  3. Get an enriched compound by providing it's id


## Example - Aspartame 

Aspartame molecular weight: 294,3 g/mol

<img width="235" alt="image" class="center" src="https://user-images.githubusercontent.com/8875161/150159541-1c9233ca-e70a-478d-82ac-75467c18110e.png">

<img width="989" alt="image" src="https://user-images.githubusercontent.com/8875161/150150632-ac0636b9-88dc-405f-92f9-33c8724632c3.png">

| True atoms number | Predicted atoms number |
| --- | --- |
| 21 | **20**  |



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
  
    curl -X GET "http://localhost:${EXSCIENTIA_ASSESMENT_WEBAPP_SERVER_PORT}/predict?molecular_weight=294.30"
  
  

## Kill Mongo DB server

    mongo exscientia --host $EXSCIENTIA_ASSESMENT_DB_URL --port $EXSCIENTIA_ASSESMENT_DB_PORT --eval "db.dropDatabase()"
    brew services stop mongodb-community
    
    
## Appendix

During Exploratory Data Analysis, we've found a high correlation between compound number of atoms and his molecular weight.
<img width="359" alt="image" src="https://user-images.githubusercontent.com/8875161/150159794-28e91d4e-64bd-4e5f-a8d1-777de5c085e8.png">


