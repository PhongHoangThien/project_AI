import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt
import numpy as np
from PIL import Image
import tensorflow as tf

import numpy
#load the trained model to classify sign
from tensorflow.keras.models import load_model
model = load_model('my_model.h5')

#dictionary to label all traffic signs class.
classes = {  
    1: 'Giới hạn tốc độ (20km/h)',
    2: 'Giới hạn tốc độ (30km/h)',      
    3: 'Giới hạn tốc độ (50km/h)',       
    4: 'Giới hạn tốc độ (60km/h)',      
    5: 'Giới hạn tốc độ (70km/h)',    
    6: 'Giới hạn tốc độ (80km/h)',      
    7: 'Hết giới hạn tốc độ (80km/h)',     
    8: 'Giới hạn tốc độ (100km/h)',    
    9: 'Giới hạn tốc độ (120km/h)',     
    10: 'Cấm vượt',   
    11: 'Cấm vượt phương tiện trên 3.5 tấn',     
    12: 'Đường ưu tiên',    
    13: 'Nhường đường tại giao lộ',     
    14: 'yield',     
    15: 'Dừng lại',       
    16: 'Cấm phương tiện',       
    17: 'Cấm phương tiện > 3.5 tấn',       
    18: 'Cấm vào',       
    19: 'Cảnh báo chung',     
    20: 'Khúc cua nguy hiểm bên trái',      
    21: 'Khúc cua nguy hiểm bên phải',   
    22: 'Cua đôi',      
    23: 'Đường gồ ghề',     
    24: 'Đường trơn',       
    25: 'Đoạn đường thu hẹp phía bên phải',  
    26: 'Công trường',    
    27: 'Đèn tín hiệu giao thông',      
    28: 'Dành cho người đi bộ',     
    29: 'Trẻ em băng qua đường',     
    30: 'Xe đạp qua đường',       
    31: 'Cảnh báo băng tuyết',
    32: 'Động vật hoang dã qua đường',      
    33: 'Hết giới hạn tốc độ và cấm vượt',      
    34: 'Quẹo phải phía trước',     
    35: 'Quẹo trái phía trước',       
    36: 'Đi thẳng',      
    37: 'Đi thẳng hoặc quẹo phải',      
    38: 'Đi thẳng hoặc quẹo trái',      
    39: 'Giữ bên phải',     
    40: 'Giữ bên trái',      
    41: 'Vòng xuyến bắt buộc',     
    42: 'Hết cấm vượt',      
    43: 'Hết cấm vượt phương tiện > 3.5 tấn'
}
                 
#initialise GUI
class TrafficSignApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nhận dạng biển báo giao thông')
        self.setGeometry(100, 100, 1000, 750)

        # Khởi tạo layout
        self.layout = QVBoxLayout(self)

        # Tiêu đề
        self.heading = QLabel('Nhận dạng biển báo giao thông', self)
        self.heading.setFont(QFont('Arial', 18, QFont.Bold))
        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setStyleSheet("color: Black; padding: -20px;")

        # Tạo bảng QTableWidget
        self.table = QTableWidget(self)
        self.table.setRowCount(4)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Tên', 'MSSV'])

        self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 200)

        self.table.setMaximumHeight(200)

        # Thêm dữ liệu vào bảng
        self.add_student_data()

        self.layout.addWidget(self.heading)
        self.layout.addWidget(self.table)

        # Upload Button
        self.upload_button = QPushButton('Upload an image', self)
        self.upload_button.setStyleSheet("background-color: #c71b20; color: white; font: bold 10pt Arial;")
        self.upload_button.clicked.connect(self.upload_image)
        self.layout.addWidget(self.upload_button)

        # Label để hiển thị hình ảnh
        self.sign_image = QLabel(self)  
        self.sign_image.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.sign_image)

        # Label kết quả phân loại
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 16, QFont.Bold))
        self.label.setStyleSheet("color: Black; ")
        self.layout.addWidget(self.label)

        # Nút Nhận dạng
        self.classify_button = QPushButton('Nhận dạng', self)
        self.classify_button.setStyleSheet("background-color: #c71b20; color: white; font: bold 10pt Arial;")
        self.classify_button.clicked.connect(self.classify_image)
        self.layout.addWidget(self.classify_button)


    def upload_image(self):
        # Mở hộp thoại để chọn file ảnh
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
    
        if file_path:
            # Lưu trữ đường dẫn file ảnh
            self.file_path = file_path  # Lưu file_path vào thuộc tính của đối tượng

            uploaded = Image.open(file_path)

            uploaded.thumbnail((self.width(), self.height()))

            # Chuyển hình ảnh từ PIL sang QPixmap
            im = QPixmap(file_path)
            im = im.scaled(360, 360, Qt.KeepAspectRatio)
            self.sign_image.setPixmap(im)

            self.label.setText("")

    def classify_image(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            self.label.setText("Chưa chọn ảnh!")
            return

        self.label.setText("Đang xử lí...")

        try:
            # Mở ảnh đã chọn
            image = Image.open(self.file_path)
            image = image.resize((30, 30))  # Resize cho phù hợp với mô hình
            image = np.expand_dims(image, axis=0)
            image = np.array(image)

            # Dự đoán lớp biển báo
            pred_probabilities = model.predict(image)[0]
            pred = pred_probabilities.argmax(axis=-1)
            sign = classes[pred + 1]

            print(f"Predicted sign: {sign}")

            self.label.setText(f"Nhận dạng biển báo: {sign}")

        except Exception as e:
            self.label.setText(f"Error: {str(e)}")

    def add_student_data(self):
        students = [
            ("Trần Ngọc Tân", "22130247"),
            ("Cao Tiến Thành", " 22130254"),
            ("Nguyễn Ngọc Thịnh", " 22130270"),
            ("Phong Hoàng Thiện", "22130264"),
        ]

        for row, student in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(student[0]))
            self.table.setItem(row, 1, QTableWidgetItem(student[1]))
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TrafficSignApp()
    window.show()
    sys.exit(app.exec_())