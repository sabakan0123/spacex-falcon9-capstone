# Falcon 9 landing analysis

This is an independent reproduction using the IBM course datasets, not the student's previous notebook submissions. Data in `dataset_part_2.csv` has 90 preselected launches from 2010–2020 and the SQL source has 101 rows; results should not be mixed. The preprocessed payload mass includes imputation performed in the course data. The 27-slide `SpaceX_capstone.pdf` summarizes the methods and results.

Install dependencies with `python -m pip install -r requirements.txt`. Open the executed `spacex_capstone.ipynb` to explore the analysis, or run `python analyze.py` to download the course data, run SQL queries and train the classifiers. The model uses an 80/20 stratified split (seed 42), four-fold training cross-validation, and a separate holdout set. One-hot encoding, imputation, and scaling are fit inside the pipeline. `model_results.json` contains the full metrics. No hyperparameter search was performed.

Run `python visual_analytics.py` to generate `launch_sites_map.html` and start the Dash app at http://127.0.0.1:8050. Stop it with Ctrl+C. These are course-era historical data, not current SpaceX performance.

The notebook, analysis scripts, map and dashboard are an independent reconstruction. They do not claim to be the original course lab notebooks. Source datasets: [modeling data](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv) and [SQL data](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_2/data/Spacex.csv). Map tiles © OpenStreetMap contributors.
