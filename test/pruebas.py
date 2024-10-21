import sqlalchemy
import pandas as pd


engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
df = pd.read_sql_query("SELECT * FROM ipi_valores", engine)
print(df)
