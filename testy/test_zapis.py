import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from baza_danych import zapisz_zmiany_w_bazie

class TestZapisuDoBazy(unittest.TestCase):

    # Używamy patch, aby przechwycić wywołanie pyodbc.connect i zapobiec prawdziwemu połączeniu z SQL
    @patch('baza_danych.zapis.pyodbc.connect')
    def test_generowanie_zapytania_update(self, mock_connect):
        # Konfiguracja fałszywego połączenia (mock)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Przygotowanie testowych danych udających wycinek Twojej tabeli z Pandas
        dane_testowe = {
            'id': [99],
            'indicator_name': ['Wskaźnik testowy'],
            'year': [2024],
            'value_change_percent': [15.5]
        }
        df = pd.DataFrame(dane_testowe)

        # Wywołanie funkcji zapisującej dla wiersza o indeksie 0
        zapisz_zmiany_w_bazie(df, row_idx=0)

        # Sprawdzenie, czy funkcja próbowała otworzyć połączenie i wykonać zapytanie
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

        # Pobranie zapytania i wartości, które funkcja próbowała wysłać do SQL
        wywolanie = mock_cursor.execute.call_args
        zapytanie_sql = wywolanie[0][0]
        wartosci = wywolanie[0][1]

        # Weryfikacja struktury zapytania SQL
        self.assertIn("UPDATE [D_UKR].[dbo].[t_tiles] SET", zapytanie_sql)
        self.assertIn("[indicator_name] = ?", zapytanie_sql)
        self.assertIn("[year] = ?", zapytanie_sql)
        czesc_set = zapytanie_sql.split("WHERE")[0]
        self.assertNotIn("[id] = ?", czesc_set)  # ID nie może być w sekcji SET
        self.assertTrue(zapytanie_sql.endswith("WHERE [id] = ?"))

        # Weryfikacja przekazanych wartości (czy ID wylądowało na samym końcu pod WHERE)
        self.assertEqual(wartosci[0], 'Wskaźnik testowy')
        self.assertEqual(wartosci[1], 2024)
        self.assertEqual(wartosci[2], 15.5)
        self.assertEqual(wartosci[-1], 99) # Ostatnia wartość w liście musi odpowiadać ID