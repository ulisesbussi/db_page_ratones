import subprocess
from dash import (
                dcc, html, Input, 
                Output, State, ctx, callback, ALL,
                register_page,
    )
import dash_bootstrap_components as dbc


#----------------------------register--------------------------
register_page(__name__, path="/",name='Comenzar experimento')
#--------------------------------------------------------------



#from .utils import read_exp_fil, write_exp_file
import page_utils

last_exp_data= page_utils.read_exp_file()



def check_if_running_exp(last_exp_data : dict, poll : int):
    if poll == None:
        name = last_exp_data.get('db_name')
        dur = last_exp_data.get('time_seg')
        return f"Corriendo el experimento {name} con duración: {dur} segs"
    return f"Experimento {last_exp_data['db_name']} finalizado"
   



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
     dcc.Interval(id = "interval-component",
         interval    = 10*1000,
         n_intervals = 0,
     ),    
     html.Div([
        html.H2(check_if_running_exp(last_exp_data,77),
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
          [Input('start-button', 'n_clicks'),
          Input('interval-component','n_intervals'),],
          State('exp-name', 'value'),
          State({'type': 'dur_dd', 'id':ALL}, 'value'),
          prevent_initial_call=True
          )

def run_experiment(click: int, inter:int , name: str, values: list):
    global last_exp_data
    global subpro
    #triggered_props = Dash.callback_context.triggered_prop_ids
    trigger_id =ctx.triggered_id
    if trigger_id =="start-button": #if click == 0:
        name = '..\\dbs\\' + name + '.db' if name != '' else '..\\dbs\\exp.db'
        
        vv = [int(v) for v in values]
        ts = vv[-1] + 60 * (vv[-2] + 60 * (vv[-3] + 24 * vv[-4]))
        last_exp_data = {'db_name': name, 'time_seg': ts}
        
        page_utils.write_exp_file(last_exp_data)    #dbname = name.split('\\')[-1]
        read_and_save_path = "C:\\Users\\Lucas\\Documents\\Lucas\\Ratones\\db_page_ratones-main\\read_and_save.py" #print(name)
        #subpro=subprocess.Popen(["python", read_and_save_path ,'-d', name, '-t', f'{ts}s'])
        subpro=subprocess.Popen(["python", read_and_save_path ,'-d', name, '-t', f'{ts}s'])
        
        return [f"Experimento corriendo {last_exp_data['db_name']}",
            check_if_running_exp(last_exp_data,subpro.poll())]
    elif trigger_id =="interval-component": 
        try:
            poll = subpro.poll()
        except:
            poll = 578 #checkear valor
            
        if poll == None:
            return ["", check_if_running_exp(last_exp_data,poll)]
        elif poll == 578:
            return ["",f"Experimento {last_exp_data['db_name']} finalizado"]
        else: return ["",f"Experimento {last_exp_data['db_name']} finalizado"]
    
    
    #run_experiment_thread(name, ts)
    
