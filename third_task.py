import sys
import requests
import argparse
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


params = argparse.ArgumentParser()
params.add_argument("--spn", default=0.005, type=float)
params.add_argument("arg", nargs='*', default=['no args'])
args = params.parse_args()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 450)
        self.change = False

        self.map = QLabel(self)
        self.map.resize(600, 450)

        self.it_max = QLabel(self)
        self.it_max.setText('Максимальное приближение.')
        self.it_max.resize(200, 25)
        self.it_max.hide()

        self.object = QLineEdit(self)
        self.object.resize(300, 25)
        self.object.move(0, 0)

        self.spn = QLineEdit(self)
        self.spn.setText('0.005')
        self.spn.move(0, 25)

        self.spn2 = QLineEdit(self)
        self.spn2.setText('0.005')
        self.spn2.move(100, 25)

        self.btn = QPushButton(self)
        self.btn.setText('Find')
        self.btn.move(200, 25)
        self.btn.clicked.connect(self.find)

    def find(self):
        global SPN, SPN2
        SPN = float(ex.spn.text())
        SPN2 = float(ex.spn2.text())

        img = QPixmap('map.png')
        self.map.setPixmap(img)
        self.object.hide()
        self.spn.hide()
        self.spn2.hide()
        self.btn.hide()
        main()

    def keyPressEvent(self, event):
        global SPN, SPN2, LL, LL_for_map
        self.it_max.hide()

        print(event.key() == Qt.Key_Up)

        if event.key() == Qt.Key_PageUp:  # too slow
            SPN -= VALUE
            SPN2 -= VALUE
            self.change = True
        elif event.key() == Qt.Key_PageDown:
            SPN += VALUE
            SPN2 += VALUE
            self.change = True

        elif event.key() == Qt.Key_Up:  # not working
            LL[1] += VALUE2
            self.change = True
        elif event.key() == Qt.Key_Down:
            LL[1] -= VALUE2
            self.change = True
        elif event.key() == Qt.Key_Right:
            LL[0] += VALUE2
            self.change = True
        elif event.key() == Qt.Key_Left:
            LL[0] -= VALUE2
            self.change = True

        if self.change:
            print(LL)
            LL_for_map = f'll={LL[0]},{LL[1]}'
            print(LL_for_map)
            try:
                img = QPixmap('map.png')
                self.map.setPixmap(img)
                main()
                self.change = False
            except Exception:
                self.it_max.show()


def geocode(address):
    geocoder_api_server = 'http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b'

    geocoder_params = {
        'api_key': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': address,
        'format': 'json'}
    response = requests.get(geocoder_api_server, params=geocoder_params)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError()

    features = json_response['response']['GeoObjectCollection']['featureMember']
    return features[0] if features else None


def get_ll_spn(address):
    global LL, LL_for_map

    toponym = geocode(address)
    if not toponym:
        return None, None
    toponym_coordinates = toponym['GeoObject']['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split(' ')

    LL = [toponym_longitude, toponym_lattitude]
    LL_for_map = f'll={toponym_longitude},{toponym_lattitude}'

    # return f'll={toponym_longitude},{toponym_lattitude}'
    return LL_for_map


def show_map(ll, map_type='map', spn_0=0.005, spn_1=0.005):
    map_params = {
        'll': ll,
        'spn': ','.join([str(spn_0), str(spn_1)]),
        'l': map_type}
    a = f'https://static-maps.yandex.ru/1.x/?{map_params["ll"]}&spn={map_params["spn"]}&l={map_params["l"]}'
    response = requests.get(a)

    if not response:
        raise RuntimeError()

    map_file = 'map.png'
    try:
        with open(map_file, 'wb') as file:
            file.write(response.content)
    except IOError():
        pass


def main():
    toponym_to_find = ex.object.text()
    if toponym_to_find:
        ll = get_ll_spn(toponym_to_find)
        spn_0 = SPN
        spn_1 = SPN2
        show_map(ll, spn_0=spn_0, spn_1=spn_1)
    else:
        print('No data')


SPN = float(0.005)
SPN2 = float(0.005)
VALUE = 0.005
VALUE2 = 0.000005
LL = [37.0, 37.0]
LL_for_map = 'll=37.0,37.0'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())
