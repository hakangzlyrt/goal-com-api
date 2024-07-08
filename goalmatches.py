import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GOAL_MACLAR_PATH = 'goal_maclar.json'
GOAL_BITMIS_MACLAR_PATH = 'goal_bitmis_maclar.json'

def save_data_to_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Veriler {file_path} dosyasına başarıyla kaydedildi.")

def read_data_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"{file_path} dosyası okunamadı: {e}")
        return []

def veri_cek():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        url = "https://www.goal.com/tr/canlı-skorlar"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="match-row"]')))

        match_rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="match-row"]')
        matches = []
        finished_matches = []

        for match in match_rows:
            try:
                takim1 = match.find_elements(By.CSS_SELECTOR, 'h4[data-testid="team-name"]')[0].text.strip()
                takim1resim = match.find_elements(By.CSS_SELECTOR, 'img[data-testid="team-crest"]')[0].get_attribute('src')
                takim2 = match.find_elements(By.CSS_SELECTOR, 'h4[data-testid="team-name"]')[1].text.strip()
                takim2resim = match.find_elements(By.CSS_SELECTOR, 'img[data-testid="team-crest"]')[1].get_attribute('src')

                ertelendi = match.find_elements(By.CSS_SELECTOR, 'span[data-testid="result-inactive-status"]')
                if ertelendi:
                    skor = "ERT"
                else:
                    takim1skor = match.find_element(By.CSS_SELECTOR, 'p.result_team-a__jx1EM').text.strip()
                    takim2skor = match.find_element(By.CSS_SELECTOR, 'p.result_team-b__kNMbF').text.strip()
                    skor = f"{takim1skor} - {takim2skor}"

                zaman_elementi = match.find_elements(By.CSS_SELECTOR, 'span[data-testid="status-full-time"], span[data-testid="status-period"], time[data-testid="status-start-date"]')
                saat = ", ".join([elem.text.strip() for elem in zaman_elementi if elem.text.strip()])

                match_info = {
                    'takim1': takim1,
                    'takim1resim': takim1resim,
                    'takim2': takim2,
                    'takim2resim': takim2resim,
                    'skor': skor,
                    'saat': saat or ""
                }

                if 'status-full-time' in [elem.get_attribute('data-testid') for elem in zaman_elementi]:
                    finished_matches.append(match_info)
                    print(f"Biten Maç: {match_info}")
                else:
                    matches.append(match_info)
                    print(f"Maç: {match_info}")

            except Exception as e:
                print(f"Maç ekleme hatası: {e}")

        driver.quit()

        if matches:
            save_data_to_file(matches, GOAL_MACLAR_PATH)
        else:
            print("Veri bulunamadı veya yapı değişti.")

        if finished_matches:
            save_data_to_file(finished_matches, GOAL_BITMIS_MACLAR_PATH)
        else:
            print("Biten maç verisi bulunamadı veya yapı değişti.")

        try:
            existing_matches = read_data_from_file(GOAL_MACLAR_PATH)
            print(f"{GOAL_MACLAR_PATH} dosyası {len(existing_matches)} eleman içeriyor.")
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

        try:
            existing_finished_matches = read_data_from_file(GOAL_BITMIS_MACLAR_PATH)
            print(f"{GOAL_BITMIS_MACLAR_PATH} dosyası {len(existing_finished_matches)} eleman içeriyor.")
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

    except Exception as e:
        print(f"Veri çekme sırasında hata oluştu: {e}")

if __name__ == "__main__":
    veri_cek()
