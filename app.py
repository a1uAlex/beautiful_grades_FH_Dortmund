from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
from pip._vendor import requests

class Klausur:
    def __init__(self, name, creditPoints, note):
        self.name = name
        self.creditPoints = creditPoints
        self.note = note

    def __repr__(self):
        return str(self.name) + ", " + str(self.creditPoints) + ", " + str(self.note)


class KlausrListe:
    def __init__(self, liste):
        self.liste = liste
        self.average = self.avg()
        self.credits = self.sum()

    def sum(self):
        sum = 0
        for klausur in self.liste:
            sum = sum + klausur.creditPoints
        return sum

    def sumOnlyGraded(self):
        sum = 0
        for klausur in self.liste:
            if klausur.note != 0:
                sum = sum + klausur.creditPoints
        return sum

    def avg(self):
        avg = 0
        for klausur in self.liste:
            avg = avg + klausur.creditPoints * klausur.note
        return int((avg / self.sumOnlyGraded()) * 10)/10

app = Flask(__name__)


@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/noten', methods=['POST'])
def noten():
    data = {
        'LIMod': '',
        'HttpRequest_PathFile': '/',
        'HttpRequest_Path': '/',
        'RemoteEndPointIP': '',
        'User': request.form['user'],
        'PWD': request.form['passwort'],
        'x': '0',
        'y': '0'
    }

    response = requests.post('https://ods.fh-dortmund.de/ods', data=data)
    soup = BeautifulSoup(response.text, 'lxml')

    if len(soup.select("form")) > 0:
        return redirect('/')

    ssid = soup.a['href'][49:]
    print(ssid)

    noten = requests.get("https://ods.fh-dortmund.de/ods?Sicht=ExcS&ExcSicht=Notenspiegel&m=1&SIDD=" + ssid)
    soup = BeautifulSoup(noten.text, 'lxml')

    studiengang = soup.select('td + td')[6].text.replace(',','')


    notenListe = soup.find(lambda tag: tag.name == "h3" and studiengang in tag.text).find_next("table").select('tr')[3:]

    klausurListe = []

    for tr in notenListe:
        name = tr.select_one('td:nth-of-type(2)').text.strip()
        note = tr.select_one('td:nth-of-type(6)').text.strip().replace(',', '.')
        if note == '':
            note = 0
        note = float(note)
        cp = float(tr.select_one('td:nth-of-type(7)').text.strip().replace(',', '.'))
        klausur = Klausur(name, cp, note)
        klausurListe.append(klausur)

    klausurListe = KlausrListe(klausurListe)
    print(klausurListe.average)
    print(klausurListe.credits)
    return render_template('noten.html', klausurListe=klausurListe)


if __name__ == '__main__':
    app.run()