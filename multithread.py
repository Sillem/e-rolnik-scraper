import threading
from selenium import webdriver
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import multiprocessing
import json
import re
from datetime import datetime
import os 
def get_update_date():
    """Funkcja która zwracać ma datę ostatniej aktualizacji działek.
    
    Ale za jednym zamachem pobieram liczbę podstron.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.page_load_strategy = 'none'
    chrome_path = ChromeDriverManager().install()
    chrome_service = Service(chrome_path)
    driver = Chrome(options=options, service=chrome_service)
    driver.implicitly_wait(10)
    driver.get("https://erolnik.gov.pl/#/dzialki/lista")
    date = driver.find_element(By.ID, "jhi-advertisement-edit-heading").text
    subpage_numbers = driver.find_elements(By.CLASS_NAME, "page-item")
    n_of_pages = max([int(x.text.replace('\n(current)', '')) for x in subpage_numbers if re.match("[0-9]{1,}", x.text)])
    #driver.close()
    return date, n_of_pages
    

    

def web_scrape(page):
    """Funkcja do scrapowania jednej podstrony z działkami z https://erolnik.gov.pl/#/dzialki/lista

    Args:
        page (int): numer pobieranej podstrony działek do adresu URL
        
    Returns:
        plik .xlsx o nazwie {page}.xlsx z działkami z danej podstrony
    """
    print(f"Obecnie pobierane strony to {page}")
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'none'
    options.add_argument("--headless=new")
    chrome_path = ChromeDriverManager().install()
    chrome_service = Service(chrome_path)
    driver = Chrome(options=options, service=chrome_service)
    strona = []
    wait_time = 5
    driver.implicitly_wait(wait_time)
    url = f"https://erolnik.gov.pl/#/dzialki/lista?page={page}&size=50&sort=id,desc"
    driver.get(url)
    breads = driver.find_elements(By.TAG_NAME, "td")
    strona = [atr.text for atr in breads]
    if strona:
        print(f"Udało się pobrać stronę {page}.")
        działki = pd.DataFrame([], index=["WOJEWÓDZTWO", "POWIAT", "GMINA", "OBRĘB", "DZIAŁKA"])
        for początek in range(0, len(strona), 11):
            działki = pd.concat([działki, pd.Series(strona[początek + 1:początek + 6],
                                                    index=["WOJEWÓDZTWO", "POWIAT", "GMINA", "OBRĘB", "DZIAŁKA"])], axis=1)
        działki.transpose().to_excel(f"exele/{page}.xlsx")
    else:
        print(f"Nie udało się pobrać strony {page}. W tym przejściu pomijam.")
    driver.close()
    

def forward_pass(skok, l_podstron):
    """Pojedyncze przejście po wszystkich podstronach e-rolnika

    Args:
        skok (int): liczba rdzeni procesora, ile podstron w jednym kroku może być przetwarzane
        l_podstron (int): liczba podstron na https://erolnik.gov.pl/#/dzialki/lista
    """
    print(f"Zaczynam pobieranie {l_podstron} stron.")
    for ostatni_w_kroku in range(skok+1,l_podstron,skok):
        # List of subpage URLs
        subpage_urls = list(range(ostatni_w_kroku-skok, ostatni_w_kroku))
        # Create and start a separate thread for each subpage
        processes = []
        for url in subpage_urls:
            process = multiprocessing.Process(target=web_scrape, args=(url,))
            process.start()
            processes.append(process)

        # Wait for all threads to complete
        for process in processes:
            process.join()
            
def fill_missing(skok, strony):
    """Odpowiednik forward passa, tylko uzupełniamy brakujące podstrony.
    
    Brakujące arkusze mogą być efektem jakichś konfliktów między wątkami i wynika z kompromisu dobranej
    zmiennej oczekiwania na odpowiedź od serwera

    Args:
        skok (int): liczba rdzeni procesora, ile podstron w jednym kroku może być przetwarzane
        strony (list): lista podstron które muszą być uzupełnione.
    """
    
    #jeżeli brakujących stron jest mniej niż 3 krotność rdzeni to nie warto się bawić w wieloprocesowość
    if len(strony) < 3*skok: 
        for page in strony:
            web_scrape(page)
    else:
        for ostatni_w_kroku in range(skok+1,len(strony),skok):
            # List of subpage URLs
            try:
                subpage_urls = strony[ostatni_w_kroku-skok:ostatni_w_kroku] #jeżeli zostało tyle podstron to załaduj wszystkie rdzenie
            except:
                subpage_urls = strony[ostatni_w_kroku-skok:len(strony)-1] #jeżeli nie to tyle ile zostało
            # Create and start a separate thread for each subpage
            processes = []
            for url in subpage_urls:
                process = multiprocessing.Process(target=web_scrape, args=(url,))
                process.start()
                processes.append(process)

            # Wait for all threads to complete
            for process in processes:
                process.join()
                
if __name__ == "__main__":
    """ 
    Główna część programu do pobierania działek. Tutaj najpierw zostanie zweryfikowane czy potrzeba aktualizować zasób,
    na postawie "Działki z zasobu wrsp z dnia ##.##.#### R.", następnie zostanie wykonany jeden forward_pass
    a następnie uzupełnione braki na podstawie zawartości folderu exele
    """
    new_date, n_of_pages = get_update_date()
    new_date = re.search("[0-9]{2}.[0-9]{2}.[0-9]{4}", new_date).group() #data ostatniej aktualizacji danych pobrana erolnika
    new_date = datetime.strptime(new_date, '%d.%m.%Y').date() #data do obiektu datetime.date
    with open('database_info.json', 'r') as file:
        current_date = datetime.strptime(json.load(file)['last_updated'], '%d.%m.%Y').date() 
    
    if(current_date < new_date):
        print(f"Zapisana baza pochodzi z {current_date}, baza z erolnika z {new_date}. Rozpoczynam aktualizację.")
    else:
        print("Obecna baza jest najnowszą wersją")
        exit()
        
    forward_pass(6, n_of_pages) #pobieranie działek do folderu exele
    
    #jakich dzialek nie pobralo?
    missing = list(set(range(1,n_of_pages+1)) - set([int(file.replace('.xlsx', '')) for file in os.listdir('exele')]))
    #nastąpi 10 prób pobrania działek które zostały
    for proba in range(10):
        if missing:
            fill_missing(6, missing)
            missing = list(set(range(1,n_of_pages+1)) - set([int(file.replace('.xlsx', '')) for file in os.listdir('exele')]))

    #jak wszystko poszło po naszej myśli, nadpisujemy datę w pliku json
    with open('database_info.json', 'w') as file:
        file.write(json.dumps({"last_updated":new_date}))
    
    print("AKTUALIZACJA PRZEBIEGŁA POMYŚLNIE, PROSZĘ O POŁĄCZENIE PLIKÓW PRZY UŻYCIU MODUŁU file_joiner.py")
        
        
    

    
    
    
    
    
