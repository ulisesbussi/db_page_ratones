import os
import json

exp_file = "/home/raspberryunq/db_page_ratones-main/dbs/last_exp.txt"

def read_exp_file():
    if os.path.exists(exp_file):
        with open(exp_file, "r") as f:
            last_exp_data = json.load(f)
    else:
        last_exp_data = {}
    return last_exp_data

def write_exp_file(last_exp_data):
    with open(exp_file, "w") as f:
        json.dump(last_exp_data, f)
    
#def read_exp_file():
   # last_exp_data = {}
   # try:
      #  if os.path.exists(exp_file):
          #  with open(exp_file, "r") as f:
         #       file_content = f.read()
        #        if file_content.strip():  # Verifica si el archivo no está vacío
       #             last_exp_data = json.loads(file_content)
      #          else:
     #               print("El archivo está vacío.")
    #except FileNotFoundError:
   #     print(f"El archivo {exp_file} no se encontró.")
  #  except json.decoder.JSONDecodeError as e:
 #       print(f"Error de formato JSON en el archivo {exp_file}: {e}")
#    return last_exp_data 
