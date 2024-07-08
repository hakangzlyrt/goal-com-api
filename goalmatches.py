import schedule
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

                # Maçın ertelenip ertelenmediğini kontrol et
                ertelendi = match.find_elements(By.CSS_SELECTOR, 'span[data-testid="result-inactive-status"]')
                if ertelendi:
                    skor = "ERT"  # Maç ertelendiyse "ERT" kullan
                else:
                    takim1skor = match.find_element(By.CSS_SELECTOR, 'p.result_team-a__jx1EM').text.strip()
                    takim2skor = match.find_element(By.CSS_SELECTOR, 'p.result_team-b__kNMbF').text.strip()
                    skor = f"{takim1skor} - {takim2skor}"

                # Zaman bilgilerini al
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

                # Maçın bitip bitmediğini kontrol et ve uygun dosyaya ekle
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
            with open('goal_maclar.json', 'w', encoding='utf-8') as f:
                json.dump(matches, f, ensure_ascii=False, indent=4)
            print("Maç verileri goal_maclar.json dosyasına başarıyla kaydedildi.")
        else:
            print("Veri bulunamadı veya yapı değişti.")

        if finished_matches:
            with open('goal_bitmis_maclar.json', 'w', encoding='utf-8') as f:
                json.dump(finished_matches, f, ensure_ascii=False, indent=4)
            print("Biten maç verileri goal_bitmis_maclar.json dosyasına başarıyla kaydedildi.")
        else:
            print("Biten maç verisi bulunamadı veya yapı değişti.")
        
        try:
            with open('goal_maclar.json', 'r', encoding='utf-8') as f:
                matches = json.load(f)
            print(f"goal_maclar.json dosyası {len(matches)} eleman içeriyor.")
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

        try:
            with open('goal_bitmis_maclar.json', 'r', encoding='utf-8') as f:
                finished_matches = json.load(f)
            print(f"goal_bitmis_maclar.json dosyası {len(finished_matches)} eleman içeriyor.")
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

    except Exception as e:
        print(f"Veri çekme sırasında hata oluştu: {e}")

def surekli_veri_cekme():
    schedule.every(1).minutes.do(veri_cek)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    surekli_veri_cekme()
