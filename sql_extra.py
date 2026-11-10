import sqlite3
import pandas as pd
from pathlib import Path
c = sqlite3.connect(Path(__file__).parent / 'spacex.db')
queries = [
    "SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE Landing_Outcome='Success (drone ship)' AND PAYLOAD_MASS__KG_ > 4000 AND PAYLOAD_MASS__KG_ < 6000",
    "SELECT TRIM(Mission_Outcome) AS outcome, COUNT(*) AS n FROM launches GROUP BY TRIM(Mission_Outcome)",
    "SELECT Date, Booster_Version, Launch_Site FROM launches WHERE Landing_Outcome='Failure (drone ship)' AND Date LIKE '2015%'",
    "SELECT TRIM(Landing_Outcome) AS outcome, COUNT(*) AS n FROM launches WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' GROUP BY TRIM(Landing_Outcome) ORDER BY n DESC"
]
for q in queries:
    print(q)
    print(pd.read_sql_query(q,c).to_string(index=False))
