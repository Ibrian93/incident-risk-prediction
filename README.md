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
