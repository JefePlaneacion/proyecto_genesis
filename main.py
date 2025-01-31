from fastapi import FastAPI, BackgroundTasks,HTTPException
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import uuid
import asyncio
import aiohttp
import time
import requests


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_data(session, url, headers, params):
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            return {"error": f"Error en la consulta: Código de estado {response.status}", "message": await response.text()}



@app.get("/api/df_opm")

async def get_df_opm():
    df_opm = pd.read_excel(r"C:\Users\JORGE CONTRERAS\OneDrive - 900208659-2 DAMIS SAS\Escritorio\PLANEACION\consumos\INDICADORES PLANEACION\METRICASALMACEN\LISTADO_OPM.xlsx")
    
    df_opm = df_opm.fillna("")
    df_opm["Referencia"] = df_opm["Referencia"].str.strip()

    df_opm = df_opm[["Fecha","O.P. Número","Estado","Referencia","Desc. Item","Bodega","U.M. ","Cant. Requerida","CATEGORIA","LINEA","FAMILIA DE PRODUCTO"]]

    return df_opm.to_dict(orient="records")



# Configuración de la API
url = "http://201.234.74.137:82/v3/ejecutarconsultaestandar"
headers = {
    'conniKey': 'Connikey-parasolestropicalesdamis-VJDSNLE1',
    'conniToken': 'VJDSNLE1UDVAOFG4SZNFMU40SDJYOFG4SZNAOESZWTHPNFO4VTDZOA'
}
params = {
    'idCompania': 6631,
    'descripcion': 'API_v2_Inventarios_InvFecha',
}
num_pag = 1  # Número de página
tam_pag = 100  # Tamaño de página
max_concurrent_tasks = 10  # Máximo de tareas concurrentes

async def fetch_page(session, num_pag):
    """
    Función para obtener una página de datos.
    """
    # Hacemos una copia de los parámetros para evitar modificar el global `params`
    params_with_paging = {**params, 'paginacion': f'numPag={num_pag}|tamPag={tam_pag}'}
    
    try:
        async with session.get(url, headers=headers, params=params_with_paging) as response:
            print(f"Consultando página {num_pag} con parámetros: {params_with_paging}")  # Depuración: Imprimir parámetros de la solicitud
            if response.status != 200:
                print(f"Error al obtener la página {num_pag}: {response.status} - {await response.text()}")
                return []
            data = await response.json()
            print(f"Respuesta de la página {num_pag}: {data}")  # Depuración: Imprimir respuesta de la API
            return data.get('data', [])  # Extrae la lista de datos de la respuesta
    except Exception as e:
        print(f"Excepción al obtener la página {num_pag}: {e}")
        return []

async def fetch_all_data():
    """
    Función principal para obtener todos los datos de forma concurrente.
    """
    base_inventario = []  # Lista para almacenar todos los datos
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            # Crear tareas para las páginas actuales
            tasks = [
                asyncio.create_task(fetch_page(session, page + i))
                for i in range(max_concurrent_tasks)
            ]
            
            # Esperar a que todas las tareas se completen
            results = await asyncio.gather(*tasks)
            
            # Agregar los datos obtenidos a la lista principal
            for result in results:
                if not result:  # Si una página no tiene datos, hemos llegado al final
                    print("No se encontraron más datos en las páginas.")
                    return base_inventario
                base_inventario.extend(result)

            # Avanzar al siguiente bloque de páginas
            page += max_concurrent_tasks


@app.get("/api/inventario")
async def obtener_inventario():
    """
    Endpoint que retorna el inventario como un DataFrame.
    """
    # Obtener todos los datos
    datos = await fetch_all_data()
    
    # Convertir los datos en un DataFrame de pandas
    df = pd.DataFrame(datos)
    
    # Convertir el DataFrame en un diccionario para enviarlo como JSON
    return df.to_dict(orient="records")


    """
    try:

        while True:
            params['paginacion'] = f'numPag={num_pag}|tamPag={tam_pag}'
            response = requests.get(url, headers=headers, params=params)
            # Verificar el código de estado
            if response.status_code == 200:
                data_inventario = response.json()
                if "detalle" in data_inventario and "Table" in data_inventario["detalle"]:
                    table_data = data_inventario["detalle"]["Table"]
                    base_invetario.extend(table_data)

                    if len(table_data) < tam_pag:
                        break
                else:
                    return {
                        "error": "La respuesta no contiene los datos esperados.",
                        "message": response.text,
                    } 
            else:
                return {
                    "error": f"Error en la consulta: Código de estado {response.status_code}",
                    "message": response.text,
                }
            num_pag += 1
        return base_invetario

    except requests.RequestException as e:
        return {
            "error": "Ocurrió un error al realizar la solicitud HTTP",
            "details": str(e),
        }
    except Exception as e:
        return {
            "error": "Ocurrió un error inesperado",
            "details": str(e),
        } 







    """
    