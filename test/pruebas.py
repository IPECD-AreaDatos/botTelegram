import sqlalchemy
import pandas as pd


engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/dwh_sociodemografico")
df = pd.read_sql_query("SELECT * FROM censo_ipecd_municipios", engine)
print(df)
municipio = "Corrientes"
datos_departamento = df[df['municipio'] == municipio]
print(datos_departamento)
