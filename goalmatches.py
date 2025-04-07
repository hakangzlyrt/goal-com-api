import json
import base64
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# GitHub API ve repository bilgileri
GITHUB_TOKEN = ''
REPO_OWNER = ''
REPO_NAME = 'goal-com-api'
FILES = {
    'goal_maclar.json': 'goal_maclar.json',
    'goal_bitmis_maclar.json': 'goal_bitmis_maclar.json'
}

# GitHub üzerinde dosya güncelleme fonksiyonu
def github_update_file(file_path, content, message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # Dosyanın mevcut SHA değerini al
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sha = response.json()['sha']

        # Dosyayı güncellemek için veriyi hazırla
        data = {
            "message": message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }

        # PUT isteği ile dosyayı güncelle
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()

        print(f"{file_path} dosyası güncellendi.")

    except requests.exceptions.RequestException as e:
        print(f"Hata oluştu: {e}")

# Veri çekme fonksiyonu
def veri_cek():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
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

        # Eski verileri oku
        try:
            with open('goal_maclar.json', 'r', encoding='utf-8') as f:
                last_matches_content = f.read()
        except FileNotFoundError:
            last_matches_content = None

        try:
            with open('goal_bitmis_maclar.json', 'r', encoding='utf-8') as f:
                last_finished_matches_content = f.read()
        except FileNotFoundError:
            last_finished_matches_content = None

        # Yeni verileri JSON formatına çevir
        matches_content = json.dumps(matches, ensure_ascii=False, indent=4)
        finished_matches_content = json.dumps(finished_matches, ensure_ascii=False, indent=4)

        # Değişiklik olup olmadığını kontrol et ve güncelle
        if matches_content != last_matches_content:
            with open('goal_maclar.json', 'w', encoding='utf-8') as f:
                f.write(matches_content)
            github_update_file(FILES['goal_maclar.json'], matches_content, "Ongoing matches updated")
            print("Maç verileri goal_maclar.json dosyasına kaydedildi ve GitHub'a güncellendi.")
        else:
            print("Maç verilerinde değişiklik yok, güncelleme yapılmadı.")

        if finished_matches_content != last_finished_matches_content:
            with open('goal_bitmis_maclar.json', 'w', encoding='utf-8') as f:
                f.write(finished_matches_content)
            github_update_file(FILES['goal_bitmis_maclar.json'], finished_matches_content, "Finished matches updated")
            print("Biten maç verileri goal_bitmis_maclar.json dosyasına kaydedildi ve GitHub'a güncellendi.")
        else:
            print("Biten maç verilerinde değişiklik yok, güncelleme yapılmadı.")

    except Exception as e:
        print(f"Veri çekme sırasında hata oluştu: {e}")

# Eğer script direk çalıştırıldıysa veri çekme işlemini başlat
if __name__ == "__main__":
    veri_cek()
