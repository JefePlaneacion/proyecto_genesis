import aiohttp
import asyncio
import pandas as pd

# Configuración de la API
url = "http://201.234.74.137:82/v3/ejecutarconsultaestandar"
headers = {
    'conniKey': 'Connikey-parasolestropicalesdamis-VJDSNLE1',
    'conniToken': 'VJDSNLE1UDVAOFG4SZNFMU40SDJYOFG4SZNAOESZWTHPNFO4VTDZOA'
}
params = {
    'idCompania': 6631,
    'descripcion': 'API_v2_Inventarios_InvFecha',
    'parametros': "f150_id=''MP002''"
}
num_pag = 1  # Número de página
tam_pag = 100  # Tamaño de página
max_concurrent_tasks = 10  # Máximo de tareas concurrentes

async def fetch_page(session, num_pag):
    """
    Función para obtener una página de datos.
    """
    # Hacemos una copia de los parámetros para evitar modificar el global `params`
    params_with_paging = {**params,'paginacion': f'numPag={num_pag}|tamPag={tam_pag}'}

    
    try:
        async with session.get(url, headers=headers, params=params_with_paging) as response:
            print(f"Consultando página {num_pag} con parámetros: {params_with_paging}")  # Depuración: Imprimir parámetros de la solicitud
            if response.status != 200:
                print(f"Error al obtener la página {num_pag}: {response.status} - {await response.text()}")
                return []
            data = await response.json()
            print(f"Respuesta de la página {num_pag}: {data}")  # Depuración: Imprimir respuesta de la API
            
            # Verifica si los datos están en la clave 'data'
            if 'detalle' not in data or 'Table' not in data['detalle']:
                print(f"Respuesta inesperada en la página {num_pag}: {data}")
                return []
                
            return data['detalle']['Table']  # Extrae la lista de datos de la respuesta

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
            print(f'resltados en {page}:{results}')
            
            # Agregar los datos obtenidos a la lista principal
            for result in results:
                if not result:  # Si una página no tiene datos, hemos llegado al final
                    print("No se encontraron más datos en las páginas.")
                    return base_inventario
                base_inventario.extend(result)

            # Avanzar al siguiente bloque de páginas
            page += max_concurrent_tasks
    return base_inventario

def obtener_dataframe():
    """
    Función para obtener los datos como un DataFrame y guardarlos en un archivo Excel.
    """
    # Ejecutar el bucle de eventos asíncronos
    datos = asyncio.run(fetch_all_data())
    print(datos)
    
    
    # Verificar si los datos están vacíos antes de intentar crear el DataFrame
    if not datos:
        print("No se obtuvieron datos.")
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay datos

    # Convertir la lista de datos en un DataFrame de pandas
    df = pd.DataFrame(datos)
    
    # Verificar el contenido del DataFrame antes de guardar
    print(f"Datos obtenidos: {len(df)} filas.")
    print(df.head())  # Imprimir las primeras filas del DataFrame para depuración
    
    df=df[df['f150_id'] == 'MP002']
    df.columns=['id_company','Bodega','Item','Cod_referencia','Ext1','Ext2','Und','Existencia','Existencia2','Cantidad_Comprometida','Cantidad_comprometida2','Cantidad_salida1','Cantidad_salida2','Cantidad_pos1','Cantidad_post2','Costo_promedio','Costo_promedio_total','id_lote','id_ubicacion']

    # Guardar el DataFrame en un archivo Excel
    df.to_excel('inventario.xlsx', index=False)  # index=False evita que se guarde el índice en el archivo Excel
    
    return df




# Uso del código
if __name__ == "__main__":
    df = obtener_dataframe()
    print(f"Datos obtenidos: {len(df)} filas.")
    print(df.head())


