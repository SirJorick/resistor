from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

# Resistor color codes
def get_color_code():
    return {
        "Black": 0,
        "Brown": 1,
        "Red": 2,
        "Orange": 3,
        "Yellow": 4,
        "Green": 5,
        "Blue": 6,
        "Violet": 7,
        "Gray": 8,
        "White": 9,
        "Gold": -1,  # Tolerance only
        "Silver": -2  # Tolerance only
    }

# Format the result for readability
def format_result(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M Ω"  # Mega-ohms
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K Ω"  # Kilo-ohms
    else:
        return f"{value} Ω"  # Ohms

# Decode SMD resistor numbers
def decode_smd_number(number):
    try:
        if len(number) == 3:  # Standard 3-digit SMD resistor
            value = int(number[:2]) * (10 ** int(number[2]))
        elif len(number) == 4:  # 4-digit precision SMD resistor
            value = int(number[:3]) * (10 ** int(number[3]))
        else:
            return "Invalid SMD format"
        return format_result(value)
    except (ValueError, IndexError):
        return "Invalid SMD format"

# Calculate resistor value based on bands
def calculate_resistor_value(bands):
    color_code = get_color_code()
    try:
        if len(bands) == 4:  # 4-band resistor
            value = (color_code[bands[0]] * 10 + color_code[bands[1]]) * (10 ** color_code[bands[2]])
            tolerance = {"Gold": 5, "Silver": 10}.get(bands[3], 20)
        elif len(bands) == 5:  # 5-band resistor
            value = (color_code[bands[0]] * 100 + color_code[bands[1]] * 10 + color_code[bands[2]]) * (10 ** color_code[bands[3]])
            tolerance = {"Gold": 5, "Silver": 10}.get(bands[4], 20)
        else:
            return "Invalid bands"
        return f"{format_result(value)} ± {tolerance}%"
    except KeyError:
        return "Invalid color band"

class ResistorCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Colorful Resistor Calculator")
        self.setStyleSheet("background-color: #f0f4f8; color: #333333;")
        self.setFont(QFont("Arial", 10))

        layout = QVBoxLayout()

        # Title
        title = QLabel("🎨 Resistor Color Coding Calculator")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4a90e2;")
        layout.addWidget(title)

        # 4-band Resistor Section
        layout.addWidget(self.create_section_label("4-Band Resistor"))
        self.band4_boxes = [self.create_colorful_combo_box() for _ in range(4)]
        self.band4_labels = [QLabel() for _ in range(4)]  # Labels to show selected color
        band4_layout = QHBoxLayout()
        for box, label in zip(self.band4_boxes, self.band4_labels):
            band4_layout.addWidget(box)
            band4_layout.addWidget(label)  # Add label next to combo box
        layout.addLayout(band4_layout)

        self.band4_result = QLabel()
        self.band4_result.setStyleSheet("font-size: 14px; color: #333333;")
        layout.addWidget(self.band4_result)

        # 5-band Resistor Section
        layout.addWidget(self.create_section_label("5-Band Resistor"))
        self.band5_boxes = [self.create_colorful_combo_box() for _ in range(5)]
        self.band5_labels = [QLabel() for _ in range(5)]  # Labels to show selected color
        band5_layout = QHBoxLayout()
        for box, label in zip(self.band5_boxes, self.band5_labels):
            band5_layout.addWidget(box)
            band5_layout.addWidget(label)  # Add label next to combo box
        layout.addLayout(band5_layout)

        self.band5_result = QLabel()
        self.band5_result.setStyleSheet("font-size: 14px; color: #333333;")
        layout.addWidget(self.band5_result)

        # SMD Resistor Section
        layout.addWidget(self.create_section_label("SMD Resistor"))
        self.smd_input = QLineEdit()
        self.smd_input.setPlaceholderText("Enter SMD Code (e.g., 102, 1003)")
        self.smd_input.textChanged.connect(self.update_smd_result)
        self.smd_input.setStyleSheet("padding: 5px; font-size: 12px; border: 1px solid #b0bec5;")
        layout.addWidget(self.smd_input)

        self.smd_result = QLabel()
        self.smd_result.setStyleSheet("font-size: 14px; color: #333333;")
        layout.addWidget(self.smd_result)

        self.setLayout(layout)

        # Connect signals for automatic computation
        for box in self.band4_boxes:
            box.currentIndexChanged.connect(self.update_4band_result)
        for box in self.band5_boxes:
            box.currentIndexChanged.connect(self.update_5band_result)

    def create_section_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 12, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #00796b; margin: 10px 0;")
        return label

    def create_colorful_combo_box(self):
        combo = QComboBox()
        color_codes = get_color_code().keys()
        combo.addItems(color_codes)
        combo.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #b0bec5;
                padding: 3px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                selection-background-color: #4caf50;
                selection-color: #ffffff;
            }
            """
        )
        return combo

    def update_band_color(self, box, label):
        # Updates the color label next to the combo box based on the selected color
        selected_color = box.currentText()

        color_mapping = {
            "Black": "#000000", "Brown": "#A52A2A", "Red": "#FF0000", "Orange": "#FFA500", "Yellow": "#FFFF00",
            "Green": "#008000", "Blue": "#0000FF", "Violet": "#8A2BE2", "Gray": "#808080", "White": "#FFFFFF",
            "Gold": "#FFD700", "Silver": "#C0C0C0"
        }

        label.setStyleSheet(f"background-color: {color_mapping.get(selected_color, '#ffffff')}; padding: 5px;")

    def update_4band_result(self):
        bands = [box.currentText() for box in self.band4_boxes]
        self.band4_result.setText(calculate_resistor_value(bands))
        # Update the color of each band label
        for box, label in zip(self.band4_boxes, self.band4_labels):
            self.update_band_color(box, label)

    def update_5band_result(self):
        bands = [box.currentText() for box in self.band5_boxes]
        self.band5_result.setText(calculate_resistor_value(bands))
        # Update the color of each band label
        for box, label in zip(self.band5_boxes, self.band5_labels):
            self.update_band_color(box, label)

    def update_smd_result(self):
        number = self.smd_input.text()
        self.smd_result.setText(decode_smd_number(number))

if __name__ == "__main__":
    app = QApplication([])
    window = ResistorCalculatorApp()
    window.show()
    app.exec_()
