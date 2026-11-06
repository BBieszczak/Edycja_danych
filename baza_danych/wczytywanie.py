import pyodbc
import pandas as pd
import warnings

#lokalne dance do połaczenai sie z baza
server = r'localhost\SQLEXPRESS'
database = 'D_UKR'

conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=' + server + ';'
                              r'DATABASE=' + database + ';'
                                                        r'Trusted_Connection=yes;'
)

try:
    print("Łączenie z bazą danych...")
    conn = pyodbc.connect(conn_str)
    print("Połączenie z bazą D_UKR nawiązane pomyślnie!\n")

    sql_query = "SELECT * FROM [D_UKR].[dbo].[t_tiles]"

    # Ignorujemy ostrzeżenie o braku SQLAlchemy
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        df = pd.read_sql(sql_query, conn)


except pyodbc.Error as e:
    print("Wystąpił błąd bazy danych (sprawdź czy usługa SQLEXPRESS jest włączona):", e)
except Exception as e:
    print("Wystąpił niespodziewany błąd:", e)

finally:
    if 'conn' in locals():
        conn.close()
        print("\nPołączenie z bazą zostało zamknięte.")
