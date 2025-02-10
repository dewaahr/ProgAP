from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import json

import smtplib
# from Tes import check_user_data

def get_presensi(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='data')
    # print(table)
    result = []
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

def cek_presensi(data_presensiLama, data_presensiBaru):
        if len(data_presensiLama) != len(data_presensiBaru):
            print("ada Presensi baru")
        else:
            print("Belum ada Presensi baru")


def get_kelas():
    login_url = "https://eclass.ukdw.ac.id/id/home/do_login"
    target_url = "https://eclass.ukdw.ac.id/e-class/id/kelas/index"
    
    user = json.load(open("user.json"))
    payload = {
        'id': user['id'],
        'password': user['password'],
        'return_url': user['return_url']
    }

    with requests.Session() as session:
        response = session.post(login_url, data=payload)
        response = session.get(target_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links_materi = soup.find_all('a', href=True)
        links_materi = [link['href'] for link in links_materi if '/e-class/materi/index/' in link['href']]
        links_presensi = []
        for link in links_materi:
            link = link.replace('materi/index', 'id/kelas/presensi')
            links_presensi.append(link)
        return links_presensi
    
def create_Email(kelas,new_presensi):

    kelas_file= json.load(open("datakelas.json"))
    user = json.load(open("user.json"))
    bot_token = user['token']
    chat_id = user['chat_id']

    msgTelegram = f"Presensi Baru Kelas {kelas_file[kelas]}\n" \
                    f"Tanggal: {new_presensi['Tanggal']}\n" \
                    f"Pertemuan Ke: {new_presensi['Pertemuan Ke']}\n" \
                    f" Link Presensi : {kelas}"
    print(msgTelegram)

    send_telegram_message(bot_token,chat_id, msgTelegram)

def send_telegram_message(bot_token,chat_id, message):
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
    for i in list_kelas:
        login_url = "https://eclass.ukdw.ac.id/id/home/do_login"
        # print(i)
        user = json.load(open("user.json"))
        payload = {
        'id': user['id'],
        'password': user['password'],
        'return_url': user['return_url']
        }
        with requests.Session() as session:
            response = session.post(login_url, data=payload)
            
            response = session.get(i)
 
            presensi = get_presensi(response.text)
            data_presensi[i] = presensi
    print(data_presensi)
    with open("dataPresensi.json", "r") as file:
        data_presensi_lama = json.load(file)
        for key in data_presensi_lama:
            # print(key)
            if key in data_presensi and data_presensi[key]:
                if data_presensi[key] != data_presensi_lama[key]:
                    # print(data_presensi[key][0])
                    presensi_baru = data_presensi[key][0]
                    create_Email(key,presensi_baru)
                    json.dump(data_presensi, open("dataPresensi.json", "w"))
                    break
main()
