"""Build a Folium launch-site map and a small Plotly Dash explorer."""
from pathlib import Path
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from math import radians, sin, cos, asin, sqrt
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'dataset_part_2.csv')

def build_map():
    m = folium.Map(location=[32,-98], zoom_start=4, tiles='OpenStreetMap')
    cluster = MarkerCluster(name='Launch records').add_to(m)
    for _, launch in df.iterrows():
        status = 'Successful' if launch.Class == 1 else 'Unsuccessful / no landing'
        folium.CircleMarker([launch.Latitude, launch.Longitude], radius=4,
            color='green' if launch.Class == 1 else 'red', fill=True,
            popup=f"Flight {launch.FlightNumber} | {launch.Date} | {launch.LaunchSite} | {status}").add_to(cluster)
    for site, group in df.groupby('LaunchSite'):
        latitude, longitude = group[['Latitude','Longitude']].iloc[0]
        successes = int(group.Class.sum())
        folium.CircleMarker([latitude,longitude],radius=10,color='#00699c',fill=True,
            popup=f'{site}: {successes}/{len(group)} first-stage landing successes',
            tooltip=f'{site}: {len(group)} launches').add_to(m)
    # Approximate coastal point from the cited course map example, not a nearest-shore search.
    start = (float(df.loc[df.LaunchSite == 'CCAFS SLC 40','Latitude'].iloc[0]),
             float(df.loc[df.LaunchSite == 'CCAFS SLC 40','Longitude'].iloc[0]))
    coast = (28.56409, -80.56806)
    lat1, lon1, lat2, lon2 = map(radians, (*start, *coast))
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    distance = 6371 * 2 * asin(sqrt(a))
    folium.Marker(coast, tooltip=f'Coastal reference: {distance:.2f} km straight line').add_to(m)
    folium.PolyLine([start, coast], color='blue', weight=3, tooltip=f'{distance:.2f} km to coastal reference').add_to(m)
    folium.LayerControl().add_to(m)
    m.save(HERE / 'launch_sites_map.html')
    detail = folium.Map(location=start, zoom_start=13, tiles='OpenStreetMap')
    folium.Marker(start, tooltip='CCAFS SLC 40 launch site').add_to(detail)
    folium.Marker(coast, tooltip=f'Coastal reference: {distance:.2f} km').add_to(detail)
    folium.PolyLine([start, coast], color='blue', weight=4, tooltip=f'{distance:.2f} km straight line').add_to(detail)
    detail.save(HERE / 'launch_proximity.html')
    print(f'CCAFS SLC 40 to approximate coastal reference: {distance:.2f} km')

def make_app():
    app=Dash(__name__)
    app.layout=html.Div([
        html.H1('Falcon 9 landing outcomes'),
        html.P('IBM course dataset: 90 launches, 2010–2020'),
        dcc.Dropdown(['All sites']+sorted(df.LaunchSite.unique()),'All sites',id='site'),
        dcc.RangeSlider(0,16000,2000,value=[0,16000],id='payload',tooltip={'placement':'bottom'}),
        html.P(id='count'),dcc.Graph(id='outcomes', style={'height':'265px'}),dcc.Graph(id='payload_plot', style={'height':'300px'}),
    ],style={'fontFamily':'Arial','maxWidth':'780px','margin':'auto'})
    @app.callback(Output('count','children'),Output('outcomes','figure'),Output('payload_plot','figure'),Input('site','value'),Input('payload','value'))
    def update(site,payload):
        data=df[df.PayloadMass.between(*payload)]
        if site!='All sites': data=data[data.LaunchSite==site]
        counts=data.Class.map({0:'Unsuccessful / no landing',1:'Successful landing'}).value_counts().rename_axis('Outcome').reset_index(name='Launches')
        pie=px.pie(counts,names='Outcome',values='Launches',title='First-stage outcomes')
        scatter=px.scatter(data,x='PayloadMass',y='Class',color=data.Class.map({0:'No successful landing',1:'Successful landing'}),hover_data=['FlightNumber','LaunchSite','Orbit'],title='Payload mass and landing outcome',labels={'PayloadMass':'Payload mass (kg)','Class':'Landing class (0 = no success, 1 = success)'})
        scatter.update_yaxes(tickmode='array',tickvals=[0,1],range=[-0.2,1.2])
        pie.update_layout(margin={'l':45,'r':15,'t':40,'b':20})
        scatter.update_layout(margin={'l':60,'r':15,'t':45,'b':50}, showlegend=False)
        return f'{len(data)} launches match the filters',pie,scatter
    return app

if __name__=='__main__':
    build_map()
    make_app().run(debug=False,host='127.0.0.1',port=8050)
