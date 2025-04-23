import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

login_url = "https://eclass.ukdw.ac.id/id/home/do_login"
target_url = "https://eclass.ukdw.ac.id/e-class/id/kelas/index"

# Format untuk user.json
default_user = {
    #data email
    "email": "email pengirim",
    "passEmail": "password Email pengirim",
    "recipient": "email penerima",

    #data login e-class
    "id": "nim/id",
    "password": "password e-class",
    "return_url": "e-class/home/"
}
def check_user_data(file_path = 'user.json'):
    if not os.path.exists(file_path):
        print("File user.json tidak ditemukan. Silakan masukkan informasi pengguna:")
        user_data = {}
        for key in default_user:
            if key == "return_url":
                user_data[key]= "e-class/home/"
            else:
                user_data[key] = input(f"Masukkan {default_user[key]}: ")
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=4)
        print("File user.json berhasil dibuat.")
    else:
        with open(file_path, 'r') as f:
            user_data = json.load(f)
    return user_data

def create_Email(subject, body, user):
    sender_email = user['email']
    sender_password = user['passEmail']
    recipient_email = user['recipient']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email berhasil dikirim")
        return True
    except Exception as e:
        print(f"Gagal mengirim email: {e}")
        return False

def main():
    user = check_user_data()
    
    payload = {
        'id': user['id'],
        'password': user['password'],
        'return_url': user['return_url']
    }
    with requests.Session() as session:
        response = session.post(login_url, data=payload)
        if "Login gagal" in response.text:
            return
        else:
            response = session.get(target_url)
            if response.ok:
                print("Berhasil mengakses halaman target!")

            else:
                exit("Gagal mengakses halaman target.")
                return

            emailMSG = ""
            soup = BeautifulSoup(response.text, 'html.parser')
            datakelas = soup.find_all('div', class_='kelas_box')
            for i in datakelas:
                data = i.text.split("\n")
                data = [item.strip() for item in data if item.strip()]
                mata_kuliah = data[0]
                jadwal = data[2]
                ruang = data[3].split('|')[1].strip()
                pengajar = data[4]
                
                emailMSG += f"Mata Kuliah: {mata_kuliah}\n"
                emailMSG += f"Jadwal: {jadwal}\n"
                emailMSG += f"Ruang: {ruang}\n"
                emailMSG += f"Pengajar: {pengajar}\n\n"
            
            create_Email("Jadwal Kuliah", emailMSG, user)

def Tes():
    payload = {
       
        'return_url': 'https://eclass.ukdw.ac.id/e-class/id/home/'

    }
    with requests.Session() as session:
        response = session.post(login_url, data=payload)
        if "Login gagal" in response.text:
            print("Login gagal, silahkan periksa kembali ID atau password.")
            return
        else:
            print("Login berhasil!")
            response = session.get(target_url)
            if response.ok:
                print("Berhasil mengakses halaman target!")
            else:
                print("Gagal mengakses halaman target.")
                
    soup = BeautifulSoup(response.text, 'html.parser')
    data_side = soup.find_all(class_="menu mc", href=True)
    link_tugas = []
    for _ in data_side:
        if 'detail_tugas' in _['href']:
            link_tugas.append(_['href'])
    tes2(link_tugas)
def tes2(links):

        with requests.Session() as session:
            response = session.post(login_url, data=payload)
            response = session.get(links[0])
            soup = BeautifulSoup(response.text, 'html.parser')
            _ = soup.find_all('tr',class_="isithread")
            _2= soup.find_all('h1')
        
            task_details = []
        for task in _:
            text = task.get_text(separator="\n", strip=True)
            task_details.append(text)

        matkul_= _2[1].get_text()
        isi_= task_details[1]
        print(isi_)

                
        


Tes()
