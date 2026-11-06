import pyodbc
import pandas as pd


def zapisz_zmiany_w_bazie(df: pd.DataFrame, row_idx: int):
    server = r'localhost\SQLEXPRESS'
    database = 'D_UKR'

    conn_str = (
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=' + server + ';'
                                  r'DATABASE=' + database + ';'
                                                            r'Trusted_Connection=yes;'
    )

    try:
        # Otwieramy nowe połączenie
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Pobieramy ID edytowanego wiersza
        record_id = int(df.at[row_idx, 'id'])

        # Wyłuskujemy nazwy wszystkich kolumn, oprócz 'id'
        kolumny_do_zmiany = [col for col in df.columns if col.lower() != 'id']

        # Budujemy część zapytania: SET [kolumna1] = ?, [kolumna2] = ? ...
        set_clause = ", ".join([f"[{col}] = ?" for col in kolumny_do_zmiany])

        # Zapytanie SQL
        query = f"UPDATE [D_UKR].[dbo].[t_tiles] SET {set_clause} WHERE [id] = ?"

        # Zbieramy zaktualizowane wartości z tabeli
        wartosci = []
        for col in kolumny_do_zmiany:
            val = df.at[row_idx, col]

            if pd.isna(val):
                wartosci.append(None)  # Zamienia puste wartości (NaN) na SQL-owe NULL
            elif hasattr(val, 'item'):
                wartosci.append(val.item())
            else:
                wartosci.append(val)

        wartosci.append(record_id)

        cursor.execute(query, wartosci)

        conn.commit()

        print(f"\n[SUKCES] Zmiany dla rekordu ID {record_id} zostały trwale zapisane w bazie MS SQL!")

    except pyodbc.Error as e:
        print(f"\n[BŁĄD SQL] Nie udało się zapisać zmian w bazie: {e}")
    except Exception as e:
        print(f"\n[BŁĄD] Wystąpił niespodziewany problem podczas zapisu: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
