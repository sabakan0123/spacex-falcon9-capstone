"""Create the consolidated notebook from the reproducible project analysis."""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

base = Path(__file__).resolve().parent
notebook = nbf.v4.new_notebook()
notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
notebook.cells = [
    nbf.v4.new_markdown_cell("# SpaceX Falcon 9 first-stage landing analysis\n\nIndependent reproduction using IBM's course datasets. `dataset_part_2.csv` has 90 model records, while the separate SQL data has 101 records. Landing outcome differs from mission outcome."),
    nbf.v4.new_code_cell("import pandas as pd\nimport sqlite3\nimport json\nfrom pathlib import Path\n\ndf = pd.read_csv('dataset_part_2.csv')\nprint(f'{len(df)} launches, {df.Date.min()} to {df.Date.max()}')\ndf[['Date', 'LaunchSite', 'Orbit', 'PayloadMass', 'Outcome', 'Class']].head()"),
    nbf.v4.new_markdown_cell("## Data collection demonstrations\n`data_collection.py` attempts the SpaceX v4 API, and falls back to the course's static API-response snapshot if the live endpoint is unavailable. It also scrapes the fixed 2021 Wikipedia revision. These two samples are not used as direct inputs to the 90-row modeling data."),
    nbf.v4.new_code_cell("api = pd.read_csv('api_launch_sample.csv')\nweb = pd.read_csv('wiki_launch_sample.csv')\nprint(f'API-response sample: {len(api)} rows; Wikipedia sample: {len(web)} rows')\nweb.head(3)"),
    nbf.v4.new_markdown_cell("## Exploratory analysis\nClass 1 includes successful ground, drone-ship or controlled ocean outcomes. Class 0 also includes records with no landing attempt."),
    nbf.v4.new_code_cell("print('Overall counts:', df.Class.value_counts().to_dict())\ndf.groupby('LaunchSite').Class.agg(launches='count', successes='sum', success_rate='mean')"),
    nbf.v4.new_code_cell("df.groupby('Orbit').Class.agg(launches='count', successes='sum', success_rate='mean').sort_values('launches', ascending=False)"),
    nbf.v4.new_markdown_cell("## SQL analysis\nThe SQL queries use a separate course CSV. Site labels and row counts are those in that source."),
    nbf.v4.new_code_cell("raw_sql = pd.read_csv('spacex_sql.csv', encoding='latin-1')\nwith sqlite3.connect(':memory:') as connection:\n    raw_sql.to_sql('launches', connection, index=False)\n    sites = pd.read_sql_query('SELECT Launch_Site, COUNT(*) AS launches FROM launches GROUP BY Launch_Site ORDER BY launches DESC', connection)\nsites"),
    nbf.v4.new_markdown_cell("## Classification\nThe script fits preprocessing within each training fold and compares models using four-fold cross-validation. It then evaluates the fixed models on an 18-row holdout. The provided CSV already includes some payload imputations."),
    nbf.v4.new_code_cell("from analyze import main\nmain()"),
    nbf.v4.new_code_cell("results = json.loads(Path('model_results.json').read_text(encoding='utf-8'))\npd.DataFrame({name: {'CV accuracy': value['cv_accuracy_mean'], 'Holdout accuracy': value['test_accuracy']} for name, value in results.items()}).T"),
    nbf.v4.new_markdown_cell("## Interactive visual analytics\nOpen `launch_sites_map.html` for the Folium map. Run `python visual_analytics.py` from the project folder to start the Dash app. See the README for setup and limitations."),
]
NotebookClient(notebook, timeout=180, kernel_name='python3', resources={'metadata': {'path': str(base)}}).execute()
nbf.write(notebook, base / 'spacex_capstone.ipynb')
print('Created and executed spacex_capstone.ipynb')
