#import dash
from dash import (
                Dash, dcc, html, Input, 
                Output, State ,callback, ALL,
                register_page,
    )
import dash_bootstrap_components as dbc


#----------------------------register--------------------------
register_page(__name__, path="/",name='Comenzar experimento')
#--------------------------------------------------------------



#from .utils import read_exp_fil, write_exp_file
import page_utils

last_exp_data= page_utils.read_exp_file()



def check_if_running_exp(last_exp_data : dict):
    if last_exp_data == {}:
        return "No hay experimento corriendo"
    name = last_exp_data.get('db_name')
    dur = last_exp_data.get('time_seg')
    return f"Corriendo el experimento {name} con duración: {dur} segs"



def get_selector(id:str ,r: int, lab: str|None = None):
    lab = id if lab is None else lab
    options = [{'value': i, 'label': f"{i} {lab}"} for i in range(r)]

    return dbc.Select(id={'type': 'dur_dd', 'id':id},
                     options=options,
                     value = str(options[0]['value']),
                     className= "dur_dd"
            )
    


layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='/assets/style.css'
    ),
    html.H1("Comienzo experimento"),
    
    html.Div([
        html.H2(check_if_running_exp(last_exp_data),
                className="running-div",
                id="running-div")
        ],
        className="running-exp"
    ),
    
    html.Div(
        dbc.CardGroup([
            dbc.Row([
                dbc.Col(dbc.Textarea(
                    id="exp-name",
                    className="mb-3",
                    placeholder="Nombre experimento",
                    value="",
                )),
                dbc.Col(get_selector("dias", 100, "Días")),
                dbc.Col(get_selector("horas", 24, "Horas")),
                dbc.Col(get_selector("minutos", 60, "Mins")),
                dbc.Col(get_selector("segundos", 60, "Segs")),
                dbc.Col(dbc.Button("Comenzar", 
                                   color="secondary", 
                                   id="start-button",
                                   n_clicks=0)),
                html.H2(children=[""], id='output'),
                html.H2(children=[""], id='exp-runing'),
            ], 
            className="row-exp",
            ),
        ])
    ),
])





@callback(Output('output', 'children'),
          [Input({'type': 'dur_dd', 'id':ALL}, 'value')],
          Input('exp-name', 'value'),
        )
def update_output(values: list, name:str):
    time_text =""
    
    for v,s in zip(values,['dias','horas','minutos','segundos']):
        time_text+= f"{v} {s}, "
    vv = [int(v) for v in values]
    ts =  vv[-1] + 60*(vv[-2] +\
         60*( vv[-3]+ 24*vv[-4])) 

    text = f"El experimento {name}.db durará {time_text[:-2]} ({ts} segs.)"
        
    return [text]



@callback([Output('exp-runing', 'children'),
           Output('running-div', 'children'),],
          Input('start-button', 'n_clicks'),
          State('exp-name', 'value'),
          State({'type': 'dur_dd', 'id':ALL}, 'value'),

          )
def run_experiment(click : int, name :str , values : list):
    if click == 0:
        return ["", check_if_running_exp(last_exp_data)]
    
    name = '..\\dbs\\' + name+ '.db' if name != '' else '..\\dbs\\exp.db'
        
    vv = [int(v) for v in values]
    ts =  vv[-1] + 60*(vv[-2] +\
         60*( vv[-3]+ 24*vv[-4])) 
    last_exp_data = {'db_name': name, 
                     'time_seg': ts,
                     }
    
    page_utils.write_exp_file(last_exp_data)
    print("Falta correr 'read_and_save.py'...")
    return [f"Experimento corriendo {last_exp_data['db_name']}",
            check_if_running_exp(last_exp_data)]
    
    #run_experiment_thread(name, ts)
    