import pandas as pd


def waliduj_wartosc(new_value: str, col_name: str, col_type) -> any:
    """
    Sprawdza i konwertuje wartość tekstową na odpowiedni typ.
    """
    # 0. Jeśli pole jest całkowicie puste, zwracamy None (w bazie zapisze się jako NULL)
    if str(new_value).strip() == "":
        return None

    # 1. Kolumny wymuszające typ liczby całkowitej
    kolumny_calkowite = ['id', 'order', 'year']
    if col_name in kolumny_calkowite:
        try:
            return int(new_value)
        except ValueError:
            raise ValueError(f"Wymagana liczba całkowita dla '{col_name}', a podano '{new_value}'")

    # 2. Kolumny procentowe
    kolumny_procentowe = ['value_change_percent', 'value_share_percent']
    if col_name in kolumny_procentowe:
        czysta_wartosc = str(new_value).replace('%', '').replace(',', '.').strip()
        try:
            return float(czysta_wartosc)
        except ValueError:
            raise ValueError(f"Wymagana liczba (np. 15.5) dla '{col_name}', a podano '{new_value}'")

    # 3. Pozostałe kolumny traktujemy jako tekst (str)
    return str(new_value)