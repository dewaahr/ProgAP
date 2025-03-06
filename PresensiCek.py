import base64 as b64, json as j, cloudscraper as c, requests as r
from bs4 import BeautifulSoup as bs

def d(x): return b64.b64decode(x).decode()
def e(x): return b64.b64encode(x.encode()).decode()

d_l = d("aHR0cHM6Ly9lY2xhc3MudWtkdy5hYy5pZC9pZC9ob21lL2RvX2xvZ2lu")
d_t = d("aHR0cHM6Ly9lY2xhc3MudWtkdy5hYy5pZC9lLWNsYXNzL2lkL2tlbGFzL2luZGV4")

def g_p(h):
    s = bs(h, 'html.parser').find('table', class_='data')
    return [{"No": c[0].text.strip(), "Tanggal": c[1].text.strip(), "Pertemuan Ke": c[2].text.strip(), "Keterangan": c[3].text.strip().replace("\n", " "), "Presensi": c[4].text.strip()} for c in [r.find_all('td') for r in s.find_all('tr')[1:]]]

def c_p(o, n): print(d("QmVsdW0gYWRhIFByZXNlbnNpIGJhcnU=") if len(o) == len(n) else d("YWRhIFByZXNlbnNpIGJhcnU="))

def g_k():
    u = j.load(open(d("dXNlci5qc29u")))
    p = {'id': u['id'], 'password': u['password'], 'return_url': u['return_url']}
    s = c.create_scraper()
    r = s.post(d_l, data=p)
    l = [l['href'] for l in bs(s.get(d_t).text, 'html.parser').find_all('a', href=True) if '/e-class/materi/index/' in l['href']]
    return [m.replace('materi/index', 'id/kelas/presensi') for m in l]

def s_t(t, c, m):
    u = f"https://api.telegram.org/bot{t}/sendMessage"
    r.post(u, data={'chat_id': c, 'text': m})

def c_e(k, p):
    u = j.load(open(d("ZGF0YWtlbGFzLmpzb24=")))
    t = j.load(open(d("dXNlci5qc29u")))
    s_t(t['token'], t['chat_id'], f"Presensi Baru Kelas {u[k]}\nTanggal: {p['Tanggal']}\nPertemuan Ke: {p['Pertemuan Ke']}\nLink Presensi : {k}")

def m():
    k = g_k()
    p = {}
    u = j.load(open(d("dXNlci5qc29u")))
    for i in k:
        s = c.create_scraper()
        s.post(d_l, data={'id': u['id'], 'password': u['password'], 'return_url': u['return_url']})
        p[i] = g_p(s.get(i).text)
    with open(d("ZGF0YVByZXNlbnNpLmpzb24="), "r") as f:
        o = j.load(f)
        for k in o:
            if k in p and p[k]:
                if p[k] != o[k]:
                    c_e(k, p[k][0])
                    j.dump(p, open(d("ZGF0YVByZXNlbnNpLmpzb24="), "w"))
                    break
m()
