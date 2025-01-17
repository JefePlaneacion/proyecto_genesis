from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import requests
import asyncio
import aiohttp

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


@app.get("/api/inventarios")


async def get_inventarios():
    
    url = "http://201.234.74.137:82/v3/ejecutarconsultaestandar"
    headers = {
        'conniKey': 'Connikey-parasolestropicalesdamis-VJDSNLE1',
        'conniToken': 'VJDSNLE1UDVAOFG4SZNFMU40SDJYOFG4SZNAOESZWTHPNFO4VTDZOA'
    }
    params = {
        'idCompania': 6631,
        'descripcion': 'API_v2_Inventarios_InvFecha',
        
        
    }
    base_inventario = []
    num_pag = 1
    tam_pag = 100
    max_concurrent_tasks= 25

    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for i in range(max_concurrent_tasks):
                params = params.copy()
                params['paginacion'] = f'numPag={num_pag + i}|tamPag={tam_pag}'
                tasks.append(fetch_data(session, url, headers, params))

            # Ejecutar solicitudes concurrentes
            responses = await asyncio.gather(*tasks)
        
            has_more_data = False
            for response in responses:
                if response.get("codigo") == 1 and response.get("mensaje") == "Consulta existente sin datos.":
                    # Caso donde el servidor indica que no hay datos para esta página
                    continue
                elif "detalle" in response and "Table" in response["detalle"]:
                    datos_pagina = response["detalle"]["Table"]
                    
                    if datos_pagina:
                        base_inventario.extend(datos_pagina)
                        has_more_data = True
                elif isinstance(response, list):
                    # Caso donde la respuesta es una lista de datos
                    print(response)
                    if response:
                        base_inventario.extend(response)
                        has_more_data = True
                else:
                    # Retornar error si la respuesta no es válida
                    return {
                        "error": "La respuesta no contiene los datos esperados.",
                        "message": response.get("message", "")
                    }
                    '''return {
                        "error": "La respuesta no contiene los datos esperados.",
                        "message": response.get("message", "")
                    }'''

            # Si ninguna página contiene más datos, detener el bucle
            if not has_more_data:
                break

            # Avanzar a las siguientes páginas
            num_pag += max_concurrent_tasks
        if not base_inventario:
            return {
                "error": "No se encontraron datos en ninguna página.",
                "message": "Todas las respuestas fueron vacías o inválidas."
            }

        # Retornar todos los datos acumulados
        return base_inventario
        
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
    