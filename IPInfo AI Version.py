from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QGuiApplication, QShortcut, QKeySequence
import requests
import webbrowser
import json
import sys


FIELDS = ("status,message,continent,continentCode,country,countryCode,region,"
          "regionName,city,district,zip,lat,lon,timezone,offset,currency,"
          "isp,org,as,asname,mobile,proxy,hosting,query")

STYLE = """
QWidget {
    background-color: #0b0b14;
    color: #e4e4e7;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}
QMainWindow { background-color: #0b0b14; }

#Title {
    font-size: 30px; font-weight: 700;
    color: #a78bfa; letter-spacing: -0.5px;
}
#Subtitle { font-size: 12px; color: #71717a; }

QLineEdit {
    background-color: #14141f;
    border: 1px solid #262636;
    border-radius: 10px;
    padding: 10px 14px;
    color: #e4e4e7;
    font-size: 14px;
    selection-background-color: #7c3aed;
}
QLineEdit:focus { border: 1px solid #7c3aed; }

QPushButton {
    background-color: #7c3aed;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    color: white;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover  { background-color: #8b5cf6; }
QPushButton:pressed{ background-color: #6d28d9; }
QPushButton:disabled {
    background-color: #1f1f2e;
    color: #52525b;
}

#SecondaryButton {
    background-color: #14141f;
    color: #e4e4e7;
    border: 1px solid #262636;
}
#SecondaryButton:hover {
    background-color: #1f1f2e;
    border: 1px solid #3f3f5e;
}
#SecondaryButton:disabled { color: #52525b; }

QFrame#Card {
    background-color: #14141f;
    border-radius: 14px;
    border: 1px solid #262636;
}

QLabel#SectionTitle {
    color: #a78bfa;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
}
QLabel#FieldLabel {
    color: #71717a;
    font-size: 12px;
    font-weight: 500;
}
QLabel#FieldValue {
    color: #e4e4e7;
    font-size: 13px;
    font-weight: 600;
}
QLabel#FooterStatus { color: #71717a; font-size: 12px; }

#CopyButton {
    background-color: transparent;
    border: 1px solid #262636;
    border-radius: 6px;
    padding: 3px 0px;
    color: #71717a;
    font-size: 11px;
    font-weight: 500;
}
#CopyButton:hover {
    background-color: #1f1f2e;
    color: #a78bfa;
    border: 1px solid #7c3aed;
}

QScrollArea { border: none; background-color: transparent; }
#ScrollContent { background: transparent; }
QScrollBar:vertical {
    background-color: transparent; width: 8px; margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #262636;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background-color: #7c3aed; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none; height: 0;
}
"""


class IPWorker(QThread):
    ok  = pyqtSignal(dict)
    err = pyqtSignal(str)

    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip

    def run(self):
        try:
            url = f"http://ip-api.com/json/{self.ip}"
            r = requests.get(url, params={"fields": FIELDS}, timeout=10)
            r.raise_for_status()
            self.ok.emit(r.json())
        except Exception as e:
            self.err.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Info")
        self.setMinimumSize(760, 720)
        self.resize(820, 800)
        self.setStyleSheet(STYLE)

        self.current_data: dict | None = None
        self.worker: IPWorker | None = None

        self._build_ui()
        self._install_shortcuts()

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("IP Info")
        title.setObjectName("Title")
        subtitle = QLabel("Look up location, ISP, and network details of any IP")
        subtitle.setObjectName("Subtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        # Search row
        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address, or leave blank for your own IP…")
        self.ip_input.returnPressed.connect(self.search)

        self.myip_btn = QPushButton("My IP")
        self.myip_btn.setObjectName("SecondaryButton")
        self.myip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.myip_btn.clicked.connect(self.get_my_ip)

        self.search_btn = QPushButton("Search")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.search)

        search_row.addWidget(self.ip_input, 1)
        search_row.addWidget(self.myip_btn)
        search_row.addWidget(self.search_btn)
        root.addLayout(search_row)

        # Scrollable cards area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("ScrollContent")
        self.cards_layout = QVBoxLayout(content)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(14)

        self._build_overview_card()
        self._build_location_card()
        self._build_network_card()
        self._build_flags_card()
        self.cards_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # Footer
        footer = QHBoxLayout()
        footer.setSpacing(10)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("FooterStatus")

        self.map_btn = QPushButton("Open in Maps")
        self.map_btn.setObjectName("SecondaryButton")
        self.map_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.map_btn.setEnabled(False)
        self.map_btn.clicked.connect(self.open_map)

        self.copy_all_btn = QPushButton("Copy as JSON")
        self.copy_all_btn.setObjectName("SecondaryButton")
        self.copy_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_all_btn.setEnabled(False)
        self.copy_all_btn.clicked.connect(self.copy_all)

        footer.addWidget(self.status_label)
        footer.addStretch()
        footer.addWidget(self.map_btn)
        footer.addWidget(self.copy_all_btn)
        root.addLayout(footer)

    def _install_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.ip_input.setFocus)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.search)

    def _make_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(9)
        t = QLabel(title.upper())
        t.setObjectName("SectionTitle")
        lay.addWidget(t)
        return card, lay

    def _add_field(self, layout: QVBoxLayout, label_text: str) -> QLabel:
        row = QHBoxLayout()
        row.setSpacing(10)

        lbl = QLabel(label_text)
        lbl.setObjectName("FieldLabel")
        lbl.setFixedWidth(120)

        val = QLabel("—")
        val.setObjectName("FieldValue")
        val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        val.setWordWrap(True)

        btn = QPushButton("Copy")
        btn.setObjectName("CopyButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedWidth(54)
        btn.clicked.connect(lambda _, v=val, b=btn: self._copy_field(v, b))

        row.addWidget(lbl)
        row.addWidget(val, 1)
        row.addWidget(btn)
        layout.addLayout(row)
        return val

    def _build_overview_card(self):
        card, lay = self._make_card("Overview")
        self.f_ip     = self._add_field(lay, "IP")
        self.f_status = self._add_field(lay, "Status")
        self.cards_layout.addWidget(card)

    def _build_location_card(self):
        card, lay = self._make_card("Location")
        self.f_country  = self._add_field(lay, "Country")
        self.f_continent= self._add_field(lay, "Continent")
        self.f_region   = self._add_field(lay, "Region")
        self.f_city     = self._add_field(lay, "City")
        self.f_district = self._add_field(lay, "District")
        self.f_zip      = self._add_field(lay, "ZIP")
        self.f_lat      = self._add_field(lay, "Latitude")
        self.f_lon      = self._add_field(lay, "Longitude")
        self.f_timezone = self._add_field(lay, "Timezone")
        self.f_offset   = self._add_field(lay, "UTC Offset")
        self.cards_layout.addWidget(card)

    def _build_network_card(self):
        card, lay = self._make_card("Network")
        self.f_isp      = self._add_field(lay, "ISP")
        self.f_org      = self._add_field(lay, "Organization")
        self.f_as       = self._add_field(lay, "AS Number")
        self.f_asname   = self._add_field(lay, "AS Name")
        self.f_currency = self._add_field(lay, "Currency")
        self.cards_layout.addWidget(card)

    def _build_flags_card(self):
        card, lay = self._make_card("Connection Flags")
        self.f_mobile  = self._add_field(lay, "Mobile")
        self.f_proxy   = self._add_field(lay, "Proxy / VPN")
        self.f_hosting = self._add_field(lay, "Hosting / DC")
        self.cards_layout.addWidget(card)

    def _copy_field(self, val_label: QLabel, btn: QPushButton):
        text = val_label.text()
        if not text or text == "—":
            return
        QGuiApplication.clipboard().setText(text)
        original = btn.text()
        btn.setText("✓")
        QTimer.singleShot(900, lambda: btn.setText(original))

    def copy_all(self):
        if not self.current_data:
            return
        QGuiApplication.clipboard().setText(json.dumps(self.current_data, indent=2, ensure_ascii=False))
        self._flash("Copied JSON to clipboard", "#10b981")

    def _flash(self, msg: str, color: str, timeout_ms: int = 1600):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color};")
        QTimer.singleShot(timeout_ms, lambda: (
            self.status_label.setText("Ready"),
            self.status_label.setStyleSheet("color: #71717a;")
        ))
        
    def get_my_ip(self):
        self.ip_input.clear()
        self.search()

    def search(self):
        if self.worker and self.worker.isRunning():
            return
        ip_text = self.ip_input.text().strip()
        self.search_btn.setEnabled(False)
        self.myip_btn.setEnabled(False)
        self.status_label.setStyleSheet("color: #a78bfa;")
        self.status_label.setText("Looking up…" if not ip_text else f"Looking up {ip_text}…")

        self.worker = IPWorker(ip_text)
        self.worker.ok.connect(self._on_ok)
        self.worker.err.connect(self._on_err)
        self.worker.start()

    def _reset_buttons(self):
        self.search_btn.setEnabled(True)
        self.myip_btn.setEnabled(True)

    def _on_ok(self, data: dict):
        self._reset_buttons()

        if data.get("status") != "success":
            msg = data.get("message", "Unknown error")
            self.f_status.setText(f"Failed — {msg}")
            self.f_status.setStyleSheet("color: #ef4444; font-weight: 600;")
            self.status_label.setText(f"Lookup failed: {msg}")
            self.status_label.setStyleSheet("color: #ef4444;")
            self.map_btn.setEnabled(False)
            self.copy_all_btn.setEnabled(False)
            return

        self.current_data = data

        self.f_ip.setText(data.get("query") or "—")
        self.f_status.setText("Success")
        self.f_status.setStyleSheet("color: #10b981; font-weight: 600;")
        
        self.f_country.setText(f"{data.get('country', '—')} ({data.get('countryCode', '—')})")
        self.f_continent.setText(f"{data.get('continent', '—')} ({data.get('continentCode', '—')})")
        self.f_region.setText(f"{data.get('regionName', '—')} ({data.get('region', '—')})")
        self.f_city.setText(data.get("city") or "—")
        self.f_district.setText(data.get("district") or "—")
        self.f_zip.setText(data.get("zip") or "—")
        self.f_lat.setText(str(data.get("lat", "—")))
        self.f_lon.setText(str(data.get("lon", "—")))
        self.f_timezone.setText(data.get("timezone") or "—")

        off = data.get("offset")
        if off is not None:
            sign = "+" if off >= 0 else "-"
            h, m = divmod(abs(int(off)) // 60, 60)
            self.f_offset.setText(f"UTC{sign}{h:02d}:{m:02d}")
        else:
            self.f_offset.setText("—")

        self.f_isp.setText(data.get("isp") or "—")
        self.f_org.setText(data.get("org") or "—")
        self.f_as.setText(data.get("as") or "—")
        self.f_asname.setText(data.get("asname") or "—")
        self.f_currency.setText(data.get("currency") or "—")
        
        self._set_flag(self.f_mobile,  data.get("mobile"))
        self._set_flag(self.f_proxy,   data.get("proxy"))
        self._set_flag(self.f_hosting, data.get("hosting"))

        self.map_btn.setEnabled(True)
        self.copy_all_btn.setEnabled(True)
        self._flash(f"Found: {data.get('query', '')}", "#10b981")

    def _set_flag(self, label: QLabel, value):
        if value:
            label.setText("Yes")
            label.setStyleSheet("color: #f59e0b; font-weight: 600;")
        else:
            label.setText("No")
            label.setStyleSheet("color: #71717a;")

    def _on_err(self, err: str):
        self._reset_buttons()
        self.status_label.setText(f"Error: {err}")
        self.status_label.setStyleSheet("color: #ef4444;")

    def open_map(self):
        if not self.current_data:
            return
        lat = self.current_data.get("lat")
        lon = self.current_data.get("lon")
        if lat is None or lon is None:
            return
        webbrowser.open(f"https://www.google.com/maps?q={lat},{lon}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
