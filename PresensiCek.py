
import cloudscraper
from bs4 import BeautifulSoup
import json
import requests

def get_presensi(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='data')
    result = []
    if table:
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            no = columns[0].text.strip()
            tanggal = columns[1].text.strip()
            pertemuan_ke = columns[2].text.strip()
            keterangan = columns[3].text.strip().replace("\n", " ")
            presensi = columns[4].text.strip()
            
            result.append({
                "No": no,
                "Tanggal": tanggal,
                "Pertemuan Ke": pertemuan_ke,
                "Keterangan": keterangan,
                "Presensi": presensi
            })
    return result

def get_kelas():
    login_url = "https://eclass.ukdw.ac.id/id/home/do_login"
    target_url = "https://eclass.ukdw.ac.id/e-class/id/kelas/index"
    
    user = json.load(open("user.json"))
    payload = {
        'id': user['id'],
        'password': user['password'],
        'return_url': user['return_url']
    }
    
    scraper = cloudscraper.create_scraper()
    response = scraper.post(login_url, data=payload)
    response = scraper.get(target_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links_materi = [link['href'] for link in soup.find_all('a', href=True) if '/e-class/materi/index/' in link['href']]
    links_presensi = [link.replace('materi/index', 'id/kelas/presensi') for link in links_materi]
    return links_presensi

def create_Email(kelas, new_presensi):
    kelas_file = json.load(open("datakelas.json"))
    user = json.load(open("user.json"))
    bot_token = user['token']
    chat_id = user['chat_id']

    msgTelegram = f"Presensi Baru Kelas {kelas_file.get(kelas, 'Unknown')} \n" \
                  f"Tanggal: {new_presensi['Tanggal']} \n" \
                  f"Pertemuan Ke: {new_presensi['Pertemuan Ke']} \n" \
                  f"Keterangan: {new_presensi['Keterangan']} \n" \
                  f"Link Presensi: {kelas}"

    send_telegram_message(bot_token, chat_id, msgTelegram)

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Pesan berhasil dikirim ke Telegram.")
    else:
        print("Gagal mengirim pesan ke Telegram:", response.text)

def main():
    list_kelas = get_kelas()
    data_presensi = {}
    scraper = cloudscraper.create_scraper()
    
    for kelas_url in list_kelas:
        user = json.load(open("user.json"))
        payload = {
            'id': user['id'],
            'password': user['password'],
            'return_url': user['return_url']
        }
        
        scraper.post("https://eclass.ukdw.ac.id/id/home/do_login", data=payload)
        response = scraper.get(kelas_url)
        presensi = get_presensi(response.text)
        data_presensi[kelas_url] = presensi
    
    with open("dataPresensi.json", "r") as file:
        data_presensi_lama = json.load(file)
        
        for key in data_presensi_lama:
            if key in data_presensi and data_presensi[key]:
                if data_presensi[key] != data_presensi_lama[key]:
                    presensi_baru = data_presensi[key][0]
                    create_Email(key, presensi_baru)
                    json.dump(data_presensi, open("dataPresensi.json", "w"))
                    break

main()
