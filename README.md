# e-rolnik scraper

 Skrypt wykorzystujący wielordzeniowość do pozyskiwania spisu wszystkich działek Skarbu Państwa z platformy e-rolnik w formie .xlsx. Źródło danych to: [https://erolnik.gov.pl/#/dzialki/lista](https://erolnik.gov.pl/#/dzialki/lista)


## Instalacja

Zalecana jest instalacja w oddzielnym środowisku *venv*. Po jego aktywacji należy pobrać potrzebne do działania pakiety za pomocą instrukcji

```
pip install -r requirements.txt
```

Do działania będzie potrzeba również przeglądarka Google Chrome. 


## Działanie

Żeby zainicjować działanie programu (a więc pobieranie podstron) należy użyć polecenia

```
python multithread.py liczba_rdzeni
```

Gdzie liczba_rdzeni powinna być liczbą pomiędzy 1, a liczbą posiadanych rdzeni fizycznych. Dla najwyższej wydajności zalecane jest użycie maksymalnej liczby dostępnych rdzeni fizycznych procesora.

**Uwaga: pobieranie kilkunastu tysięcy podstron może zająć nawet wiele godzin. Zalecane jest nieużywanie komputera w tym czasie**

Po zakończonej pracy (i max. 10 cyklach uzupełniających) zostanie wyświetlony komunikat: *"AKTUALIZACJA PRZEBIEGŁA POMYŚLNIE, PROSZĘ O POŁĄCZENIE PLIKÓW PRZY UŻYCIU MODUŁU file_joiner.py"*

W tym momencie, wykonywanie programu powinno zakończyć się, a w folderze *exele* powinien znajdować się zbiór plików .xlsx o nazwach od 1 do numeru ostatniej podstrony. Każdy plik odpowiada zawartością określonej podstronie z https://erolnik.gov.pl/#/dzialki/lista. Do złączenia wszystkich plików w jeden plik należy użyć polecenia:

```
python file_joiner.py
```

Efektem działania tego polecenia będzie plik *cala_baza_erolnik.xlsx* ze wszystkimi działkami.
