import unittest
from edycja.walidacja import waliduj_wartosc


class TestWalidatoraBazy(unittest.TestCase):

    def test_puste_pola_zwracaja_none(self):
        # Sprawdzamy, czy funkcja poprawnie interpretuje puste miejsca jako NULL (None)
        self.assertIsNone(waliduj_wartosc("", "value_change_percent", None))
        self.assertIsNone(waliduj_wartosc("   ", "year", None))
        # Test na tabulatory i znaki nowej linii
        self.assertIsNone(waliduj_wartosc(" \t \n ", "description_pl", None))

    def test_kolumny_liczbowe_calkowite(self):
        # Poprawne wartości (w tym ze spacjami wokół)
        self.assertEqual(waliduj_wartosc("2024", "year", None), 2024)
        self.assertEqual(waliduj_wartosc(" 5 ", "order", None), 5)
        self.assertEqual(waliduj_wartosc("123", "id", None), 123)

        # Oczekiwane wyrzucenie błędu ValueError przy niepoprawnych danych
        with self.assertRaises(ValueError):
            waliduj_wartosc("rok 2024", "year", None)  # tekst z liczbą
        with self.assertRaises(ValueError):
            waliduj_wartosc("2024.5", "year", None)  # ułamek w miejscu na liczbę całkowitą
        with self.assertRaises(ValueError):
            waliduj_wartosc("20,5", "order", None)  # przecinek w miejscu na liczbę całkowitą

    def test_kolumny_procentowe_i_zmiennoprzecinkowe(self):
        # Testowanie różnego zapisu ułamków
        self.assertEqual(waliduj_wartosc("15.5", "value_change_percent", None), 15.5)
        self.assertEqual(waliduj_wartosc("15,5", "value_share_percent", None), 15.5)
        self.assertEqual(waliduj_wartosc(" 12% ", "value_change_percent", None), 12.0)
        self.assertEqual(waliduj_wartosc("-5,2%", "value_share_percent", None), -5.2)

        # Całkowite liczby w polach procentowych (np. dokładnie 100%)
        self.assertEqual(waliduj_wartosc("0", "value_change_percent", None), 0.0)
        self.assertEqual(waliduj_wartosc("100", "value_share_percent", None), 100.0)

        # Błędy, które powinny zostać zablokowane
        with self.assertRaises(ValueError):
            waliduj_wartosc("brak danych", "value_change_percent", None)
        with self.assertRaises(ValueError):
            waliduj_wartosc("15.5.5", "value_share_percent", None)  # za dużo kropek

    def test_kolumny_tekstowe(self):
        # Zwykły tekst powinien zostać zwrócony bez zmian
        oczekiwany_tekst = "Urodzeni w Ukrainie"
        self.assertEqual(waliduj_wartosc(oczekiwany_tekst, "description_pl", None), oczekiwany_tekst)

        # Testowanie polskich znaków diakrytycznych
        self.assertEqual(waliduj_wartosc("Zażółć gęślą jaźń", "info_pl", None), "Zażółć gęślą jaźń")

        # Liczby lub procenty wpisane w pole tekstowe (powinny być zamienione na string)
        self.assertEqual(waliduj_wartosc("123", "teryt", None), "123")
        self.assertEqual(waliduj_wartosc("15.5%", "value_pl", None), "15.5%")


if __name__ == "__main__":
    unittest.main()