# Workplace Severe Injury Risk Intelligence

This project builds an end-to-end data science pipeline using public OSHA Severe Injury Report data.

The objective is to transform public workplace injury reports into an analytical dataset that can support safety risk exploration, severity classification, and business-facing dashboards.

## Data Source

The dataset comes from OSHA Severe Injury Reports. OSHA requires employers to report severe work-related injuries such as amputations, in-patient hospitalizations, or loss of an eye. The reporting requirement began on January 1, 2015.

The raw data is not committed to this repository. Instead, it can be downloaded from OSHA using:

```bash
python src/download_data.py