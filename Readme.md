# Data Pipeline Summary

For detailed implementation and usage instructions, please refer to the [complete documentation](https://seed-waitress-434.notion.site/Weekly-Assignment-1-f9296628decd44ba988e408b1cc31ea8?pvs=4) provided.

This repository contains a data pipeline designed to manage the flow of data through various stages, from data extraction to storage and analysis. Below is a summary of the pipeline's key steps:

1. **Data Extraction**: The pipeline begins by retrieving a dataset in CSV format.

2. **Data Loading**: The dataset is then loaded into a PostgreSQL database.

3. **Data Transformation**: Transformation processes are applied to clean the data, including adjusting data types and proportions.

4. **Data Export**: The transformed data is exported from the on-premise database to Google Cloud Storage in SQL format.

5. **Data Migration**: Data from the transformed on-premise database is migrated to PostgreSQL Cloud SQL as staging data.

6. **Data Flow Management**: The pipeline's data flow is managed using either Dataflow for orchestrated batch processing or Datastream for continuous data streaming, enabling real-time analysis.

7. **Data Warehousing**: The final dataset is stored in Google BigQuery as part of the data warehouse.

This pipeline facilitates efficient data processing, transformation, and analysis, enabling organizations to derive insights from their data effectively. 

---
*Note: This README.md provides a summary of the data pipeline. For detailed information and instructions, refer to the [complete documentation](https://seed-waitress-434.notion.site/Weekly-Assignment-1-f9296628decd44ba988e408b1cc31ea8?pvs=4) and code in the repository.*
