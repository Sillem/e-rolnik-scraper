import pandas as pd
import os
"""Prosty moduł do łączenia exceli powstałych w wyniku działania głównego programu

Excele z folderu ./exele są łączone w jeden plik cala_baza_erolnik.xlsx. Używamy go po użyciu multithread.py
"""
 
# we get all the numbers of pages from the folder exele
def join_exels():
    pages_numbers = [int(x.replace('.xlsx', '')) for x in os.listdir('exele')]

    total = pd.DataFrame({}, columns=["WOJEWÓDZTWO", "POWIAT", "GMINA", "OBRĘB", "DZIAŁKA"])
    for page in range(min(pages_numbers), max(pages_numbers)+1):
        print(page)
        total = pd.concat([total, pd.read_excel(f'exele/{page}.xlsx')])

    total.to_excel('cala_baza_erolnik.xlsx')

join_exels()