import dash
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
from plotly.subplots import make_subplots


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"], suppress_callback_exceptions=True)

# Cargar archivo CSV
df = pd.read_csv('Data/datos-graficas.csv') 


with open('GeoJSON/map-campeche.geojson') as f:
    geojson_data = json.load(f)

# Configuración de opciones
municipios = df['Municipio'].unique()
years = sorted(df['Año'].unique())
delitos_options = {bien: df[df['Bien jurídico afectado'] == bien]['Tipo de delito'].unique().tolist() for bien in df['Bien jurídico afectado'].unique()}
subdelitos_options = {tipo: df[df['Tipo de delito'] == tipo]['Subtipo de delito'].unique().tolist() for tipo in df['Tipo de delito'].unique()}
modalidades_options = {(bien, tipo, subdelito): df[(df['Bien jurídico afectado'] == bien) & (df['Tipo de delito'] == tipo) & (df['Subtipo de delito'] == subdelito)]['Modalidad'].unique().tolist() for bien in df['Bien jurídico afectado'].unique() for tipo in delitos_options[bien] for subdelito in subdelitos_options[tipo]
}

custom_style = {
    'font-family': 'Quattro Slab, serif',
    'backgroundColor': '#F9F9F9',
    'padding': '10px'
}


# Layout de la página
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(src='assets/LOGO_FGECAM.png', height="70px"),  
                        width="auto"
                    ),
                    dbc.Col(
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink("Inicio", href="/")),
                                dbc.NavItem(dbc.NavLink("Estadísticas", href="/estadisticas")),
                            ],
                            navbar=True,
                            className="ms-auto"  
                        ),
                        width="auto"
                    ),
                ],
                align="center",
                className="g-0"
            )
        ],
        fluid=True
    ),
    color="#10312B",
    dark=True,
)

# Define el pie de página
footer = html.Div(
    dbc.Row(
        [
            dbc.Col(
                html.Img(src='assets/JAGUAR.png', height="70px"),  
                width={"size": 2, "offset": 0},  
                className="text-center"  
            ),
            dbc.Col(
                [
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink(html.I(className="fab fa-facebook"), href="https://www.facebook.com/GobiernoDeCampeche/?locale=es_LA", external_link=True)),
                            dbc.NavItem(dbc.NavLink(html.I(className="fab fa-twitter"), href="https://x.com/ucscampeche?lang=es", external_link=True)),
                            dbc.NavItem(dbc.NavLink(html.I(className="fab fa-instagram"), href="https://www.instagram.com/gobiernodecampeche/", external_link=True)),
                            dbc.NavItem(dbc.NavLink(html.I(className="fab fa-tiktok"), href="https://www.tiktok.com/@gobiernodetodos", external_link=True)),
                        ],
                        navbar=True,
                        className="text-start"  
                    )
                ],
                width={"size": 2, "offset": 0}  
            )
        ],
        justify="between",  
        className="py-2"  
    ),
    style={
        "backgroundColor": "#AB9470",  
        "color": "white",               
        "width": "100%",                
        "position": "relative",          
        "bottom": "0",                  
        "padding": "0"                 
    },
)

inicio_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Fiscalía General del Estado de Campeche", style={
                'color': '#53565A',
                'font-size': '36px',
                'font-weight': 'bold',
                'margin-top': '20px',
                'text-align': 'center',
                'font-family': 'Quattro Slab, serif'
            })
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Mapa de los Municipios de Campeche", style={'text-align': 'center', 'font-family': 'Quattro Slab, serif'}),
            dcc.Graph(id="mapa-campeche", figure={}, config={"displayModeBar": False}),
        ], width=8),
        dbc.Col([
            html.H3("Seleccione un año y un tipo de delito para ver las estadísticas", style={'text-align': 'center', 'font-family': 'Quattro Slab, serif'}),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(year), "value": year} for year in years],
                placeholder="Seleccione un año",
                style={"width": "100%", 'font-family': 'Quattro Slab, serif'}
            ),
            dcc.Dropdown(
                id="delito-dropdown",
                options=[{'label': delito, 'value': delito} for delito in df['Tipo de delito'].unique()],
                placeholder="Seleccione un delito",
                style={"margin-top": "20px", "width": "100%", 'font-family': 'Quattro Slab, serif'}
            ),
            dcc.Graph(id="grafica-estadisticas", style={'margin-top': '20px', 'display': 'none'}),
            html.Button("Otra Selección", id="otra-seleccion-btn", style={
                'margin-top': '20px',
                'background-color': '#9F2241',
                'color': 'white',
                'border-radius': '15px',
                'border': 'none',
                'padding': '10px 15px',
                'font-family': 'Quattro Slab, serif'
            }),
            dcc.Dropdown(
                id="year-dropdown-otra",
                options=[{"label": str(year), "value": year} for year in years],
                placeholder="Seleccione otro año",
                style={"margin-top": "20px", "display": 'none', "width": "100%", 'font-family': 'Quattro Slab, serif'}
            ),
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="mapa-campeche-otra", figure={}, style={'margin-top': '20px', 'display': 'none', 'height': '400px', 'font-family': 'Quattro Slab, serif'}), width=8),
        dbc.Col(dcc.Graph(id="grafica-estadisticas-otra", style={'margin-top': '20px', 'display': 'none', 'height': '400px', 'font-family': 'Quattro Slab, serif'}), width=4),
    ], style={'height': '450px'})  
], fluid=True)

estadisticas_layout = dbc.Container([
    dbc.Row([
        dbc.Col([dcc.Dropdown(id="bien-juridico-dropdown",
                               options=[{"label": bien, "value": bien} for bien in delitos_options.keys()],
                               placeholder="Seleccione Bien Jurídico",
                               clearable=False,
                               style={"width": "100%", "margin-bottom": "15px"})], width=4),
        dbc.Col([dcc.Dropdown(id="municipio-dropdown",
                               options=[{"label": municipio.capitalize(), "value": municipio} for municipio in municipios],
                               placeholder="Seleccione Municipio",
                               clearable=False,
                               style={"width": "100%", "margin-bottom": "15px"})], width=4),
        dbc.Col([dcc.Dropdown(id="year-dropdown-estadisticas",
                               options=[{"label": str(year), "value": year} for year in years],
                               placeholder="Seleccione Año",
                               clearable=False,
                               style={"width": "100%", "margin-bottom": "15px"})], width=4),
    ], justify="center", style={"padding-top": "20px"}),
    
    dbc.Row([
        dbc.Col([dcc.Dropdown(id="delitos-dropdown",
                               placeholder="Seleccione Tipo de Delito",
                               clearable=False,
                               style={"width": "100%", "margin-bottom": "15px"})], width=6),
        dbc.Col([dcc.Dropdown(id="subdelitos-dropdown",
                               placeholder="Seleccione Subtipo de Delito",
                               clearable=False,
                               style={"width": "100%", "margin-bottom": "15px"})], width=6),
    ], justify="center"),
    
    dbc.Row([
        dbc.Col(id="modalidades-container", style={"margin-top": "20px"})  # Contenedor para los botones
    ]),
    
    dbc.Row([
        dbc.Col([dcc.Graph(id="estadisticas-grafica", style={'margin-top': '20px'})])
    ]),
    
    dbc.Row([
        dbc.Col([html.Button("Otra Selección", id="otra-seleccion-btn", style={
            'margin-top': '20px',
            'background-color': '#9F2241',
            'color': 'white',
            'border-radius': '15px',
            'border': 'none',
            'padding': '10px 15px',
            'font-family': 'Quattro Slab, serif'
        })], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([dcc.Dropdown(id="estadisticas-year-dropdown-otra",
                               options=[],
                               placeholder="Seleccione otro año",
                               clearable=False,
                               style={"width": "100%", "margin-top": "15px", "display": "none"})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([dcc.Graph(id="estadisticas-grafica-otra", style={'margin-top': '20px', 'display': 'none'})])
    ])
], style=custom_style)

# Actualizar la función para crear el mapa de Campeche sincronizado con la gráfica
@app.callback(
    [Output("grafica-estadisticas", "figure"),
     Output("grafica-estadisticas", "style"),
     Output("mapa-campeche", "figure"),
     Output("delito-dropdown", "value")],
    [Input("year-dropdown", "value"),
     Input("delito-dropdown", "value")]
)
def actualizar_grafica_y_mapa(year, delito):
    fig_mapa_base = px.choropleth(
        geojson=geojson_data,
        locations=[feature['properties']['NOM_MUN'] for feature in geojson_data['features']],
        featureidkey="properties.NOM_MUN",
        color_discrete_sequence=["lightgray"],
        title="Mapa de municipios de Campeche"
    )
    
    fig_mapa_base.update_geos(fitbounds="locations", visible=False)
    fig_mapa_base.update_layout(mapbox_style="carto-positron", mapbox_zoom=7,
                                mapbox_center={"lat": 19.8301, "lon": -90.5349},
                                font=dict(family="Quattro Slab, serif"))

    if year and delito:
        df_filtrado = df[(df['Año'] == year) & (df['Tipo de delito'] == delito)]
        df_agrupado = df_filtrado.groupby('Municipio')[['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']].sum()
        df_agrupado['total_delitos'] = df_agrupado.sum(axis=1)
        df_agrupado = df_agrupado.reset_index()

        fig_barras = px.bar(
            df_agrupado,
            x='total_delitos',
            y='Municipio',
            orientation='h',
            color='total_delitos',
            color_continuous_scale='RdYlGn_r',
            labels={'total_delitos': 'Total de Delitos', 'Municipio': 'Municipio'},
            title=f"Total de delitos por municipio en {year}"
        )
        fig_barras.update_layout(font=dict(family="Quattro Slab, serif"))

        fig_mapa = px.choropleth(
            df_agrupado,
            geojson=geojson_data,
            locations="Municipio",
            featureidkey="properties.NOM_MUN",
            color="total_delitos",
            color_continuous_scale="RdYlGn_r",
            labels={'total_delitos': 'Total de Delitos'},
            title=f"Mapa de municipios con total de delitos en {year}"
        )

        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(mapbox_style="carto-positron", mapbox_zoom=7,
                               mapbox_center={"lat": 19.8301, "lon": -90.5349},
                               font=dict(family="Quattro Slab, serif"))

        return fig_barras, {'margin-top': '20px', 'display': 'block'}, fig_mapa, delito

    return {}, {'display': 'none'}, fig_mapa_base, None

@app.callback(
    [Output("year-dropdown-otra", "style"),
     Output("grafica-estadisticas-otra", "style"),
     Output("mapa-campeche-otra", "style")],
    [Input("otra-seleccion-btn", "n_clicks")]
)
def mostrar_otra_seleccion(n_clicks):
    if n_clicks:
        return {"margin-top": "20px", "display": 'block'}, {"margin-top": "20px", "display": 'block'}, {"margin-top": "20px", "display": 'block'}
    return {"margin-top": "20px", "display": 'none'}, {"margin-top": "20px", "display": 'none'}, {"margin-top": "20px", "display": 'none'}

@app.callback(
    [Output("grafica-estadisticas-otra", "figure"),
     Output("mapa-campeche-otra", "figure")],
    [Input("year-dropdown-otra", "value"),
     Input("delito-dropdown", "value")]
)
def actualizar_grafica_y_mapa_otra(year, delito):
    if year and delito:
        df_filtrado = df[(df['Año'] == year) & (df['Tipo de delito'] == delito)]
        df_agrupado = df_filtrado.groupby('Municipio')[['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']].sum()
        df_agrupado['total_delitos'] = df_agrupado.sum(axis=1)
        df_agrupado = df_agrupado.reset_index()

        fig_barras = px.bar(
            df_agrupado,
            x='total_delitos',
            y='Municipio',
            orientation='h',
            color='total_delitos',
            color_continuous_scale='RdYlGn_r',
            labels={'total_delitos': 'Total de Delitos', 'Municipio': 'Municipio'},
            title=f"Total de delitos por municipio en {year}"
        )
        fig_barras.update_layout(font=dict(family="Quattro Slab, serif"))


        fig_mapa = px.choropleth(
            df_agrupado,
            geojson=geojson_data,
            locations="Municipio",
            featureidkey="properties.NOM_MUN",
            color="total_delitos",
            color_continuous_scale="RdYlGn_r",
            labels={'total_delitos': 'Total de Delitos'},
            title=f"Mapa de municipios con total de delitos en {year}"
        )

        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(mapbox_style="carto-positron", mapbox_zoom=7,
                               mapbox_center={"lat": 19.8301, "lon": -90.5349},
                               font=dict(family="Quattro Slab, serif"))

        return fig_barras, fig_mapa

    return {}, {}

@app.callback(
    Output("year-dropdown-otra", "options"),
    [Input("year-dropdown", "value")]
)
def actualizar_year_dropdown_otra(year):
    if year:
        return [{"label": str(y), "value": y} for y in years if y != year]
    else:
        return [{"label": str(y), "value": y} for y in years]

# Actualizar lista de delitos según bien jurídico
@app.callback(
    Output("delitos-dropdown", "options"),
    Output("delitos-dropdown", "value"),
    Input("bien-juridico-dropdown", "value")
)
def update_delitos(bien_juridico):
    if bien_juridico:
        tipos_delito = delitos_options[bien_juridico]  
        return [{"label": tipo, "value": tipo} for tipo in tipos_delito], tipos_delito[0]  
    return [], None

@app.callback(
    Output("subdelitos-dropdown", "options"),
    Output("subdelitos-dropdown", "value"),
    Input("delitos-dropdown", "value")
)
def update_subdelitos(tipo_delito):
    if tipo_delito:
        subdelitos = subdelitos_options.get(tipo_delito, [])
        return [{"label": subdelito, "value": subdelito} for subdelito in subdelitos], subdelitos[0] if subdelitos else None
    return [], None

@app.callback(
    Output("modalidades-container", "children"),
    Input("subdelitos-dropdown", "value"),
    Input("delitos-dropdown", "value"),
    Input("bien-juridico-dropdown", "value")
)
def update_modalidades(subdelito, tipo_delito, bien_juridico):
    if subdelito and tipo_delito and bien_juridico:
        modalidades = df[(df['Bien jurídico afectado'] == bien_juridico) & 
                           (df['Tipo de delito'] == tipo_delito) & 
                           (df['Subtipo de delito'] == subdelito)]['Modalidad'].unique()
        
        if len(modalidades) > 0:  # Verificar que haya modalidades
            # Crear botones para cada modalidad
            return [html.Button(modalidad, id={'type': 'modalidad-button', 'index': modalidad}, 
                                style={"margin": "5px", 
                                       "background-color": "#9F2241", 
                                       "color": "white", 
                                       "font-family": "Quattro Slab, serif", 
                                       "border-radius": "15px",
                                       "padding": "10px 20px"}) for modalidad in modalidades]
    
    
    # Si no hay modalidades, devolver un mensaje
    return [html.Div("No hay modalidades disponibles.")]

@app.callback(
    Output("estadisticas-grafica", "figure"),
    Input("bien-juridico-dropdown", "value"),
    Input("municipio-dropdown", "value"),
    Input("year-dropdown-estadisticas", "value"),
    Input("delitos-dropdown", "value"),
    Input("subdelitos-dropdown", "value"),
    Input({"type": "modalidad-button", "index": dash.dependencies.ALL}, "n_clicks")  
)
def update_graph(bien_juridico, municipio, year, tipo_delito, subdelito, n_clicks):
    # Verificar si hay valores seleccionados
    if not bien_juridico or not municipio or not year or not tipo_delito or not subdelito:
        return {
            'data': [],
            'layout': {
                'title': "Seleccione todos los filtros",
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Total de Delitos'},
                'font': {'family': 'Quattro Slab, serif'}, 
            }
        }

    # Verificar si hubo clic en alguno de los botones de modalidad
    modalidad_seleccionada = None
    if n_clicks and any(n_clicks):  
        # Obtener el contexto activado
        triggered_context = dash.callback_context.triggered
        if triggered_context and len(triggered_context) > 0:
            triggered_id = triggered_context[0]['prop_id'].split('.')[0]
            # Convertir el ID en un diccionario
            try:
                modalidad_seleccionada = json.loads(triggered_id)['index']
            except (KeyError, json.JSONDecodeError):
                modalidad_seleccionada = None
            
    # Filtrar los datos según los filtros seleccionados
    filtered_data = df[(df['Bien jurídico afectado'] == bien_juridico) &
                         (df['Municipio'] == municipio) &
                         (df['Año'] == year) &
                         (df['Tipo de delito'] == tipo_delito) &
                         (df['Subtipo de delito'] == subdelito)]

    if modalidad_seleccionada:
        filtered_data = filtered_data[filtered_data['Modalidad'] == modalidad_seleccionada]

    # Verificar si hay datos filtrados
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {
                'title': "No hay datos para mostrar",
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Total de Delitos'},
                'font': {'family': 'Quattro Slab, serif'}, 
            }
        }

    # Sumar los delitos por mes
    monthly_totals = filtered_data.iloc[:, 6:].sum().reset_index()
    monthly_totals.columns = ['mes', 'total delitos']

    # Crear la figura
    figure = {
        'data': [{
            'x': monthly_totals['mes'],
            'y': monthly_totals['total delitos'],
            'type': 'bar',  
            'name': modalidad_seleccionada if modalidad_seleccionada else tipo_delito,  
            'text': monthly_totals['total delitos'],  
            'textposition': 'auto',
            'marker': {
            'color': monthly_totals['total delitos'],  
            'colorscale': [
                [0, '#888B8D'],  
                [0.33, '#235B4E'],  
                [0.66, '#BCA986'],  
                [1, '#9F2241']  
            ],
        } 
        }],
        'layout': {
            'title': f"Total de Delitos en {municipio} en {year}: {tipo_delito} - {subdelito} - {modalidad_seleccionada}" if modalidad_seleccionada else f"Total de Delitos por Mes: {tipo_delito} - {subdelito}",
            'xaxis': {'title': 'Meses'},
            'yaxis': {'title': 'Total de Delitos'},
            'font': {'family': 'Quattro Slab, serif'}, 
        }
    }

    return figure

@app.callback(
    Output("estadisticas-year-dropdown-otra", "options"),
    Output("estadisticas-year-dropdown-otra", "style"),
    Input("otra-seleccion-btn", "n_clicks"),
    Input("year-dropdown-estadisticas", "value")
)
def update_year_dropdown_otra(n_clicks, year):
    if n_clicks:
        return [{"label": str(y), "value": y} for y in years if y != year], {"width": "100%", "margin-top": "15px", "display": "block"}
    return [], {"width": "100%", "margin-top": "15px", "display": "none"}

@app.callback(
    Output("estadisticas-grafica-otra", "figure"),
    Output("estadisticas-grafica-otra", "style"),
    Input("bien-juridico-dropdown", "value"),
    Input("municipio-dropdown", "value"),
    Input("estadisticas-year-dropdown-otra", "value"),
    Input("delitos-dropdown", "value"),
    Input("subdelitos-dropdown", "value"),
    Input({"type": "modalidad-button", "index": dash.dependencies.ALL}, "n_clicks")  
)
def update_graph_otra(bien_juridico, municipio, year, tipo_delito, subdelito, n_clicks):
    if not year:
        return {}, {"margin-top": "20px", "display": "none"}

    # Verificar si hay valores seleccionados
    if not bien_juridico or not municipio or not year or not tipo_delito or not subdelito:
        return {
            'data': [],
            'layout': {
                'title': "Seleccione todos los filtros",
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Total de Delitos'},
                'font': {'family': 'Quattro Slab, serif'}, 
            }
        }, {"margin-top": "20px", "display": "block"}

    # Verificar si hubo clic en alguno de los botones de modalidad
    modalidad_seleccionada = None
    if n_clicks and any(n_clicks):  
        triggered_context = dash.callback_context.triggered
        if triggered_context and len(triggered_context) > 0:
            triggered_id = triggered_context[0]['prop_id'].split('.')[0]
            # Convertir el ID en un diccionario
            try:
                modalidad_seleccionada = json.loads(triggered_id)['index']
            except (KeyError, json.JSONDecodeError):
                modalidad_seleccionada = None  
                
    # Filtrar los datos según los filtros seleccionados
    filtered_data = df[(df['Bien jurídico afectado'] == bien_juridico) &
                         (df['Municipio'] == municipio) &
                         (df['Año'] == year) &
                         (df['Tipo de delito'] == tipo_delito) &
                         (df['Subtipo de delito'] == subdelito)]

    if modalidad_seleccionada:
        filtered_data = filtered_data[filtered_data['Modalidad'] == modalidad_seleccionada]

    # Verificar si hay datos filtrados
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {
                'title': "No hay datos para mostrar",
                'xaxis': {'title': 'Meses'},
                'yaxis': {'title': 'Total de Delitos'},
                'font': {'family': 'Quattro Slab, serif'}, 
            }
        }, {"margin-top": "20px", "display": "block"}

    # Sumar los delitos por mes
    monthly_totals = filtered_data.iloc[:, 6:].sum().reset_index()
    monthly_totals.columns = ['mes', 'total delitos']

    # Crear la figura
    figure = {
        'data': [{
            'x': monthly_totals['mes'],
            'y': monthly_totals['total delitos'],
            'type': 'bar',  
            'name': modalidad_seleccionada if modalidad_seleccionada else tipo_delito,  
            'text': monthly_totals['total delitos'],  
            'textposition': 'auto',
            'marker': {
            'color': monthly_totals['total delitos'],  
            'colorscale': [
                [0, '#888B8D'],  
                [0.33, '#235B4E'],  
                [0.66, '#BCA986'],  
                [1, '#9F2241']  
            ],
        } 
        }],
        'layout': {
            'title': f"Total de Delitos en {municipio} en {year}: {tipo_delito} - {subdelito} - {modalidad_seleccionada}" if modalidad_seleccionada else f"Total de Delitos por Mes: {tipo_delito} - {subdelito}",
            'xaxis': {'title': 'Meses'},
            'yaxis': {'title': 'Total de Delitos'},
            'font': {'family': 'Quattro Slab, serif'}, 
        }
    }

    return figure, {"margin-top": "20px", "display": "block"}

# Navegación de páginas
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/estadisticas":
        return estadisticas_layout
    else:
        return inicio_layout

# Layout principal de la aplicación
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    html.Div(id="page-content"),
    footer 
])

if __name__ == "__main__":
    app.run_server(debug=True)