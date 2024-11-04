# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import json
import smtplib

def get_presensi(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='data')
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

def create_Email(kelas, new_presensi):
    kelas_file = json.load(open("datakelas.json"))
    user = json.load(open("user.json"))
    sender_email = user['email']
    sender_password = user['passEmail']
    recipient_email = user['recipient']
    bot_token = user['token']
    chat_id = user['chat_id']

    msgTelegram = f"Presensi Baru Kelas {kelas_file[kelas]}\n\n" \
                    f"Tanggal: {new_presensi['Tanggal']}\n" \
                    f"Pertemuan Ke: {new_presensi['Pertemuan Ke']}\n"\
                    f" Link Presensi : {kelas}"
    send_telegram_message(bot_token,chat_id, msgTelegram)

    # msg = MIMEMultipart()
    # msg['From'] = sender_email
    # msg['To'] = recipient_email
    # msg['Subject'] = "Presensi Baru Kelas " + kelas_file[kelas]

    # body = (
    #     f"Tanggal: {new_presensi['Tanggal']}\n"
    #     f"Mata Kuliah: {kelas_file[kelas]}\n"
    #     f"Pertemuan Ke: {new_presensi['Pertemuan Ke']}\n"
    # )

    # msg.attach(MIMEText(body, 'plain'))

    # try:
    #     with smtplib.SMTP('smtp.gmail.com', 587) as server:
    #         server.starttls()
    #         server.login(sender_email, sender_password)
    #         server.send_message(msg)
    #     print("Email berhasil dikirim")
    #     return True
    # except Exception as e:
    #     print(f"Gagal mengirim email: {e}")
    #     return False

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
def send_telegram_message(bot_token,chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
    }
    response = requests.post(url, data=payload)

def main():
    list_kelas = get_kelas()
    data_presensi = {}
    for i in list_kelas:
        user = json.load(open("user.json"))
        payload = {
            'id': user['id'],
            'password': user['password'],
            'return_url': user['return_url']
        }
        with requests.Session() as session:
            response = session.post("https://eclass.ukdw.ac.id/id/home/do_login", data=payload)
            response = session.get(i)
            presensi = get_presensi(response.text)
            data_presensi[i] = presensi
            
    try:
        with open("dataPresensi.json", "r") as file:
            data_presensi_lama = json.load(file)
    except FileNotFoundError:
        data_presensi_lama = {}

    for key in data_presensi_lama:
        if data_presensi.get(key) != data_presensi_lama.get(key):
            presensi_baru = data_presensi[key][0]
            create_Email(key, presensi_baru)

    with open("dataPresensi.json", "w") as file:
        json.dump(data_presensi, file, indent=4)

main()
