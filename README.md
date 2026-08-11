# Workplace Severe Injury Intelligence

An end-to-end Data and Machine Learning Engineering project built with public OSHA Severe Injury Report data.

I chose this dataset because it is closely related to a domain I have worked with professionally. During my time in Roche's Global SHE (Safety, Health and Environment) organization, I contributed to data products used for safety reporting and decision-making.

This project gives me the opportunity to work with a familiar business domain while building the complete technical workflow myself: from raw data ingestion and data quality to analytical modelling, machine learning and, eventually, model deployment.

The project is being developed incrementally, with each stage documented as I build it.

---

## Project Objective

The dataset contains severe workplace injuries reported to OSHA.

Because the dataset already represents severe injury cases, the initial machine learning problem is **not** to predict whether an arbitrary workplace incident will become severe.

Instead, the first modelling objective is to classify the outcome of an already reported severe injury.

The current binary target is:

- `1` — the case involved an amputation or loss of an eye
- `0` — the reported severe injury did not contain either of those outcomes

This target may evolve as the project develops and the data is better understood.

Beyond model performance, the project focuses on building a reproducible data and ML workflow that could realistically support a production system.

---

## Data Source

The project uses the public [OSHA Severe Injury Report](https://www.osha.gov/severeinjury) dataset.

OSHA requires employers to report certain severe work-related injuries, including:

- in-patient hospitalizations
- amputations
- loss of an eye

The reporting requirement began on January 1, 2015.

The raw dataset is not committed to this repository.

It can be downloaded directly from OSHA by running:

```bash
python src/download_data.py
```

## Current Architecture

The project currently follows an ELT workflow.

```
OSHA Severe Injury Reports
          │
          ▼
     Raw CSV data
          │
          ▼
        DuckDB
          │
          ▼
      Raw layer
          │
          ▼
     Staging layer
          │
          ▼
   Analytical models
          │
          ├──────────────► Exploratory analysis
          │
          ▼
    ML feature dataset
          │
          ▼
    Model development
```

This architecture will evolve as additional ML engineering components are introduced.

The goal is to keep ingestion, transformation, analytics and machine learning responsabilities separated instead of building the entire workflow inside a single notebook.


## Technology Stack

### Data Engineering 
* Python
* SQL
* DuckDB
* dbt
    
### Data Analysis & Machine Learning
* Python
* Pandas
* scikit-learn
* matplotlib

Additional ML Engineering tools will be introduced as the project progress


## Current Data Models

The current transformation flow is:

* raw_severe_injuries
* stg_severe_injuries
* fct_injury_cases
* ml_injury_features

### `raw_severe_injuries`
Raw OSHA data loaded into DuckDB with minimal modification.

### `stg_severe_injuries`
Cleans and standardizes the source data, including:
* column naming
* date parsing
* data type conversion
* null handling
* standardized injury attributes

### `fct_injury_cases`
Represents reported severe injury cases and introduces analytical attributes such as:
* event year
* event month
* day of week
* NAICS industry levels
* injury outcome measures
* initial ML target

The intended grain is:
One row per OSHA severe injury report


### `ml_injury_features`
Provides a consumer-specific dataset for machine learning.
This layer contains the candidate features and target used during model development and is kept separate from the analytical models so that ML-specific transformations can evolve independently. 


## Project Progress

## Day 1 - Data Ingestion

* Downloaded the public OSHA Severe Injury Report dataset
* Loaded the raw CSV data into DuckDB
* Created the intial raw and staging tables
* Resolved date parsing issues in the source data
* Defined the first binary ML target: `high_severity_outcome`

## Day 2 - Exploratory Data Analysis
* Analysed the target distribution
* Explored injury cases per year and state
* Analysed event types, body parts and injury sources
* Created initial visualisation
* Identified data quality issues
* Documented potential modelling considerations

## Day 3 - Data Modelling * Quality
In progress.

The focus of this stage is to turn the initial SQL transformations into a structured and testable data modelling workflow before model training begins.

## ML Engineering Roadmap
The planned workflow is:
```
Data ingestion
      ↓
Data validation
      ↓
Data transformation
      ↓
ML feature dataset
      ↓
Baseline model
      ↓
Feature engineering
      ↓
Model comparison
      ↓
Model evaluation
      ↓
Experiment tracking
      ↓
Model packaging
      ↓
Inference API
      ↓
Containerized deployment
```

The goal is not only to train a model but to understand and implement the engineering lifecycle around it. 

## Modelling Considerations
One important part of this project is identifying situations where apparently useful features could produce misleading model performance
For example, the OSHA dataset contains a free-text injury narrative. Since the narrative may explicitly describe the final injury outcome, using it directly could introduce target leakage.
For this reason, text-based features will initially be excluded from the baseline model and evaluated separately later in the project.


## Repository Structure
The repository is being reorganized as the project evolves. The intended structure is:
```
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── ingestion/
│   ├── training/
│   └── inference/
│
├── dbt/
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       ├── marts/
│       └── ml/
│
├── notebooks/
│
├── tests/
│
├── README.md
└── requirements.txt
```

## Why I am building This

My professional background is primarily in data and analytics engineering, while my academic background in Mathematics and computational engineering included machine learning, optimization and numerical methods.
I am building this project to connect those two areas: using the data engineering practices I have worked with profesionally while developing stronger hands-on experience with the machine learning lifecycle.