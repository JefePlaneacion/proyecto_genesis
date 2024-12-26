from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/df_opm")

async def get_df_opm():
    df_opm = pd.read_excel(r"C:\Users\JORGE CONTRERAS\OneDrive - 900208659-2 DAMIS SAS\Escritorio\PLANEACION\consumos\INDICADORES PLANEACION\METRICASALMACEN\LISTADO_OPM.xlsx")
    
    df_opm = df_opm.fillna("")
    df_opm["Referencia"] = df_opm["Referencia"].str.strip()

    df_opm = df_opm[["Fecha","O.P. Número","Estado","Referencia","Desc. Item","Bodega","U.M. ","Cant. Requerida","CATEGORIA","LINEA","FAMILIA DE PRODUCTO"]]

    return df_opm.to_dict(orient="records")



