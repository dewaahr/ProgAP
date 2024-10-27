import requests
from bs4 import BeautifulSoup
import json
import os
import time
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
            #https://eclass.ukdw.ac.id/e-class/id/kelas/presensi/TI9493

        links_materi = soup.find_all('a', href=True)
        links_materi = [link['href'] for link in links_materi if '/e-class/materi/index/' in link['href']]
        links_presensi = []
        for link in links_materi:
            link = link.replace('materi/index', 'id/kelas/presensi')
            links_presensi.append(link)
        return links_presensi
                    

def main():
    list_kelas = get_kelas()
    # print(list_kelas)
    for i in list_kelas:
        target_url = i
        # target_url = "https://eclass.ukdw.ac.id/e-class/id/kelas/presensi/TI0043"
        login_url = "https://eclass.ukdw.ac.id/id/home/do_login"
        user = json.load(open("user.json"))
        payload = {
        'id': user['id'],
        'password': user['password'],
        'return_url': user['return_url']
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
                    return

                presensi = get_presensi(response.text)
                print (presensi)
        
# while True:        
#     presensiLama = main()
#     time.sleep(10)
#     presensiBaru = main()
#     cek_presensi(presensiLama, presensiBaru)

# get_kelas()
main()