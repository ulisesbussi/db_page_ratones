from dash import (
                dcc, html, Input, 
                Output, State, ctx, callback, ALL,
                register_page,
    )
import dash_bootstrap_components as dbc
import subprocess

"""Importo las librerias necesarias a utilizar"""
#----------------------------register--------------------------
register_page(__name__, path="/",name='Comenzar experimento')
#--------------------------------------------------------------
import page_utils 
# last_exp_data= page_utils.read_exp_file()


def check_if_running_exp(last_exp_data : dict):
    print("check running..")
    print(last_exp_data.get("Running") is None)
    if last_exp_data.get("Running") is None:
        """Mientras el Script de read_and_save este corriendo"""
        name = last_exp_data.get('db_name')
        dur = last_exp_data.get('time_seg')
        return f"Corriendo el experimento {name} con duración: {dur} segs"
    elif last_exp_data.get("Running") == 578 :
        return f"Experimento {last_exp_data['db_name']} finalizado"
    return f"Experimento {last_exp_data['db_name']} detenido"

def get_selector(id:str ,r: int, lab: str= None):
    """?"""
    lab = id if lab is None else lab
    options = [{'value': i, 'label': f"{i} {lab}"} for i in range(r)]

    return dbc.Select(id={'type': 'dur_dd', 'id':id},
                     options=options,
                     value = str(options[0]['value']),
                     className= "dur_dd"
            )

"""Defino el layout de la pestaña"""

layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='/assets/style.css'
    ),
    html.H1("Comienzo experimento"),
     dcc.Interval(id = "interval-component",
         interval    = 5*1000,
         n_intervals = 0,
     ),    
     html.Div([
        html.H2(check_if_running_exp(last_exp_data= page_utils.read_exp_file()),
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
                dbc.Col(dbc.Button("Detener", 
                                   color="danger", 
                                   id="stop-button",
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

"""Este callback corre cuando pasa el tiempo del intervalo definido o 
cuando se le da comienzo a algun exp"""
@callback([Output('exp-runing', 'children'),
           Output('running-div', 'children'),],
          [Input('start-button', 'n_clicks'),
          Input('interval-component','n_intervals'),
          Input('stop-button','n_clicks'),],
          State('exp-name', 'value'),
          State({'type': 'dur_dd', 'id':ALL}, 'value'),
          prevent_initial_call=True
          #prevent_initial_call=False
          )

def run_experiment(click: int, inter:int ,click2: int, name: str, values: list):
    global last_exp_data
    trigger_id = ctx.triggered_id
    if trigger_id =="start-button": #if click == 0:
        #name = '../dbs/' + name + '.db' if name != '' else '../dbs/exp.db'
        name = name if name!='' else 'exp'
        name = f'/home/raspberryunq/db_page_ratones-main/dbs/{name}.db'
        vv = [int(v) for v in values]
        ts = vv[-1] + 60 * (vv[-2] + 60 * (vv[-3] + 24 * vv[-4]))
        last_exp_data = {'db_name': name, 'time_seg': ts}
        page_utils.write_exp_file(last_exp_data)
        read_and_save_path = "/home/raspberryunq/db_page_ratones-main/read_and_save.py" #print(name)
        subprocess.Popen(["python3.11", read_and_save_path ,'-d', name, '-t', f'{ts}s'])
        return [f"Experimento corriendo {last_exp_data['db_name']}",
            check_if_running_exp(last_exp_data)] 
    elif trigger_id == "stop-button":
        last_exp_data["Running"]= 77
        page_utils.write_exp_file(last_exp_data)
        return ["",check_if_running_exp(last_exp_data)]
    
    else:    
        last_exp_data= page_utils.read_exp_file()
        # if last_exp_data.get("Running") is None:
        #     return ["", check_if_running_exp(last_exp_data)]
        # else: 
        return ["",check_if_running_exp(last_exp_data)]

