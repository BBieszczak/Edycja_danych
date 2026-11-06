from baza_danych import df
from baza_danych import zapisz_zmiany_w_bazie
from edycja import waliduj_wartosc


def wybierz_wskaznik(dane):
    unique_indicators = dane['indicator_name'].drop_duplicates().reset_index(drop=True)

    for i, name in unique_indicators.items():
        print(f"[{i}] {name}")

    try:
        choice_idx = int(input("\nWpisz numer wskaźnika, który chcesz wybrać: "))
        selected_indicator = unique_indicators.iloc[choice_idx]
        print(f"\nWybrano: {selected_indicator}")
        return selected_indicator
    except (ValueError, IndexError):
        print("Błąd: Podano nieprawidłowy numer.")
        return None


def wybierz_rekord(dane, selected_indicator):
    filtered_df = dane[dane['indicator_name'] == selected_indicator]

    print(f"\nZnalezione wpisy dla '{selected_indicator}':")
    for index, row in filtered_df.iterrows():
        desc = row.get('description_pl', 'Brak opisu')
        year = row.get('year', 'Brak roku')
        print(f"Index: [{index}] | Rok: {year} | Opis: {desc}")

    try:
        row_idx = int(input("\nWpisz 'Index' rekordu, który chcesz edytować: "))
        if row_idx not in filtered_df.index:
            raise ValueError("Podany Index nie znajduje się na liście.")
        return row_idx
    except ValueError as e:
        print(f"Błąd: {e}")
        return None


def przeprowadz_edycje_wiersza(dane, row_idx):
    print("\nWpisz nową wartość i wciśnij ENTER. Jeśli chcesz zostawić starą wartość, wciśnij ENTER.")

    for col in dane.columns:
        if col.lower() == 'id':
            continue

        current_value = dane.at[row_idx, col]
        new_value = input(f"{col} [{current_value}]: ")

        if new_value.strip() != "":
            col_type = dane[col].dtype
            try:
                parsed_value = waliduj_wartosc(new_value, col, col_type)
                dane.at[row_idx, col] = parsed_value
            except ValueError as e:
                error_msg = str(e) if str(e) else "nieprawidłowy format"
                print(
                    f" [!] Błąd dla kolumny '{col}': Wartość '{new_value}' jest niepoprawna ({error_msg}). Pominięto.")

    print("\nAktualnie wpisane wartości dla wybranego wiersza:")
    updated_row = dane.loc[row_idx]
    for col_name, val in updated_row.items():
        print(f" - {col_name}: {val}")


def uruchom_kreator_edycji():

    # Wybór wskaźnika
    wskaznik = wybierz_wskaznik(df)
    if not wskaznik:
        return

    # Wybór wiersza
    row_idx = wybierz_rekord(df, wskaznik)
    if row_idx is None:
        return

    # Edycja wiersza
    przeprowadz_edycje_wiersza(df, row_idx)

    # Zapis do bazy
    print("\nTrwa zapisywanie zmian na serwerze...")
    zapisz_zmiany_w_bazie(df, row_idx)

