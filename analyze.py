"""Reproduce the figures and model metrics used in the accompanying presentation."""
from pathlib import Path
import json
import sqlite3
import pandas as pd
import requests
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

HERE = Path(__file__).resolve().parent
DATA_URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv'
SQL_URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_2/data/Spacex.csv'

def download(url, path):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    path.write_bytes(response.content)

def main():
    download(DATA_URL, HERE / 'dataset_part_2.csv')
    download(SQL_URL, HERE / 'spacex_sql.csv')
    df = pd.read_csv(HERE / 'dataset_part_2.csv')
    sql = pd.read_csv(HERE / 'spacex_sql.csv', encoding='latin-1')
    print('DATA', df.shape, df.Date.min(), df.Date.max(), 'CLASS', df.Class.value_counts().to_dict())
    print('SITE',df.groupby('LaunchSite').Class.agg(['count','sum','mean']).to_string())
    print('ORBIT',df.groupby('Orbit').Class.agg(['count','sum','mean']).to_string())
    df['Year'] = pd.to_datetime(df.Date).dt.year
    print('YEAR',df.groupby('Year').Class.agg(['count','sum','mean']).to_string())
    print('REUSE',df.groupby('Reused').Class.agg(['count','sum','mean']).to_string())
    print('SQL_COLUMNS',sql.columns.tolist(), 'ROWS',len(sql))
    with sqlite3.connect(HERE / 'spacex.db') as conn:
        sql.to_sql('launches', conn, if_exists='replace',index=False)
        queries = {
            'sites': 'SELECT Launch_Site, COUNT(*) AS launches FROM launches GROUP BY Launch_Site ORDER BY launches DESC',
            'nasa_payload': "SELECT ROUND(SUM(PAYLOAD_MASS__KG_), 2) AS payload_kg FROM launches WHERE Customer = 'NASA (CRS)'",
            'booster_average': "SELECT ROUND(AVG(PAYLOAD_MASS__KG_), 2) AS avg_payload_kg FROM launches WHERE Booster_Version LIKE 'F9 v1.1%'",
            'outcomes': 'SELECT Mission_Outcome, COUNT(*) AS launches FROM launches GROUP BY Mission_Outcome ORDER BY launches DESC',
        }
        for name, query in queries.items():
            try: print('SQL',name,pd.read_sql_query(query,conn).to_string(index=False))
            except Exception as exc: print('SQL ERROR',name,str(exc))

    features = ['PayloadMass','Flights','ReusedCount','Block','Reused','Orbit','LaunchSite']
    x, y = df[features].copy(), df['Class'].astype(int)
    x['Reused'] = x['Reused'].astype(str)
    train_x, test_x, train_y, test_y = train_test_split(x,y,test_size=.2,random_state=42,stratify=y)
    numeric=['PayloadMass','Flights','ReusedCount','Block']
    categorical=['Reused','Orbit','LaunchSite']
    preprocess=ColumnTransformer([
        ('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),numeric),
        ('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore'))]),categorical),
    ])
    models={'Majority baseline':DummyClassifier(strategy='most_frequent'), 'Logistic regression':LogisticRegression(max_iter=2000,random_state=42), 'SVM':SVC(kernel='rbf'), 'Decision tree':DecisionTreeClassifier(max_depth=3,random_state=42), 'KNN':KNeighborsClassifier(n_neighbors=5)}
    cv=StratifiedKFold(n_splits=4,shuffle=True,random_state=42)
    results={}
    for name,model in models.items():
        pipe=Pipeline([('preprocess',preprocess),('model',model)])
        scores=cross_val_score(pipe,train_x,train_y,cv=cv,scoring='accuracy')
        pipe.fit(train_x,train_y)
        pred=pipe.predict(test_x)
        results[name]={'cv_accuracy_mean':float(scores.mean()),'cv_accuracy_std':float(scores.std()),'test_accuracy':float(accuracy_score(test_y,pred)),'confusion_matrix':confusion_matrix(test_y,pred,labels=[0,1]).tolist(),'test_report':classification_report(test_y,pred,output_dict=True,zero_division=0)}
    (HERE/'model_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('MODELS',json.dumps(results,indent=2))

if __name__ == '__main__': main()
