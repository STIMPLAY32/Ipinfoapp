from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import requests
import webbrowser

map_link = None

old_ip = None

def ipdata(ip):
    global map_link
    response = requests.get(f"http://ip-api.com/json/{ip}").json()
    ipwid.setText(f"IP: {ip}")
    status.setText(f"Status: {response['status']}")
    if response['status'] == "success":
        map_link = f"https://www.google.com/maps?q={response['lat']},{response['lon']}"

        status.setText(f"Status: {response['status']}")
        status.setStyleSheet("color: green;")

        country.setText(f"Country: {response['country']}")
        countrycodeandregione.setText(f"Country code / Region: {response['countryCode']}/{response['region']}")
        cityregionname.setText(f"City / Region name: {response['city']}/{response['regionName']}")
        zipcode.setText(f"ZIP Code: {response['zip']}")
        CoordinatesLat.setText(f"Coordinates (Latitude): {response['lat']}")
        CoordinatesLon.setText(f"Coordinates (Longitude): {response['lon']}")
        Timezone.setText(f"Timezone: {response['timezone']}")
        ispname.setText(f"ISP Name: {response['isp']}")
        isporg.setText(f"ISP Organization: {response['org']}")
        asnumnam.setText(f"AS Number and Name: {response['as']}")

        mainline.addWidget(ipwid, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(status, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(country, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(countrycodeandregione, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(cityregionname, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(zipcode, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(CoordinatesLat, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(CoordinatesLon, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(Timezone, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(ispname, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(isporg, alignment=Qt.AlignmentFlag.AlignCenter)
        mainline.addWidget(asnumnam, alignment=Qt.AlignmentFlag.AlignCenter)
    
    else:
        status.setText(f"Status: {response['status']}")
        status.setStyleSheet("color: red;")
        country.setText(f"Country: Error")
        countrycodeandregione.setText(f"Country code / Region:: Error")
        cityregionname.setText(f"City / Region name: Error")
        zipcode.setText(f"ZIP Code: Error")
        CoordinatesLat.setText(f"Coordinates (Latitude): Error")
        CoordinatesLon.setText(f"Coordinates (Longitude): Error")
        Timezone.setText(f"Timezone: Error")
        ispname.setText(f"ISP Name: Error")
        isporg.setText(f"ISP Organization: Error")
        asnumnam.setText(f"AS Number and Name: Error")

def sendcomand():
    global old_ip
    needip = ip.text()
    if needip == old_ip:
        webbrowser.open(map_link)
    else:
        old_ip = needip
    ipdata(needip)

app = QApplication([])
window = QWidget()
window.setFixedSize(700, 500)
window.setWindowTitle("IP Info")

status = QLabel("IP not found")
ipwid = QLabel("IP: ")
status = QLabel("IP: ")
country = QLabel("IP: ")
countrycodeandregione = QLabel("IP: ")
cityregionname = QLabel("IP: ")
zipcode = QLabel("zip code: ")
CoordinatesLat = QLabel("zip code: ")
CoordinatesLon = QLabel("zip code: ")
Timezone = QLabel("zip code: ")
ispname = QLabel("zip code: ")
isporg = QLabel("zip code: ")
asnumnam = QLabel("zip code: ")


mainline = QVBoxLayout()
ipline = QHBoxLayout()

maintitle = QLabel("IP Info")
maintitle.setStyleSheet("font-size: 30px;")
maintitle.setAlignment(Qt.AlignmentFlag.AlignCenter)


mainline.addWidget(maintitle, alignment=Qt.AlignmentFlag.AlignTop)
mainline.addLayout(ipline)


ip = QLineEdit()
enter = QPushButton("Enter")

ip.setFixedWidth(200) 

ipline.addSpacing(200)

ipline.addWidget(ip)
ipline.addWidget(enter)

ipline.addStretch() 

window.setLayout(mainline)

enter.clicked.connect(sendcomand)

window.show()
app.exec()