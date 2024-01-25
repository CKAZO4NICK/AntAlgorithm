import json
from math import ceil

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, \
    QPushButton, QComboBox, QStackedWidget, QMessageBox, QHBoxLayout
from os.path import exists
from osmr import get_car_distance_between
from ant_colony import AntColonyOptimizer


class CityNamesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cities = [
            ("Вінниця", 49.234390408511814, 28.47014834191607, 3),  # Вінниця
            ("Дніпро", 48.46627860973343, 35.05047285876131, 8),  # Дніпро
            ("Донецьк", 48.02185385051659, 37.80677952391504, 10),  # Донецьк
            ("Житомир", 50.25339316207128, 28.657924172264067, 3),  # Житомир
            ("Запоріжжя", 47.831382036476356, 35.1189888173966, 8),  # Запоріжжя
            ("Київ", 50.45134961642491, 30.528562328861973, 5),  # Київ
            ("Кропивницький", 48.508274229237664, 32.25582951950288, 3),  # Кропивницький
            ("Луцьк", 50.746627182170364, 25.32662283541708, 2),  # Луцьк
            ("Миколаїв", 46.9666948711213, 31.997001674192823, 4),  # Миколаїв
            ("Одеса", 46.48491710873236, 30.735124364674036, 4),  # Одеса
            ("Полтава", 49.586659936105654, 34.54625007685097, 4),  # Полтава
            ("Рівне", 50.62046149279269, 26.25017502178829, 3),  # Рівне
            ("Сімферополь", 44.95359394386997, 34.10165971029707, 10),  # Сімферополь
            ("Суми", 50.90929654076946, 34.793269176862566, 5),  # Суми
            ("Тернопіль", 49.552579302037145, 25.591488651525612, 3),  # Тернопіль
            ("Ужгород", 48.62187086048696, 22.28427190821433, 1),  # Ужгород
            ("Харків", 49.99932999001834, 36.243244251247496, 6),  # Харків
            ("Херсон", 46.63660127380812, 32.617222405317825, 8),  # Херсон
            ("Хмельницький", 49.422158893104786, 26.982555067429676, 3),  # Хмельницький
            ("Черкаси", 49.44539187571886, 32.06364735364304, 3),  # Черкаси
            ("Чернівці", 48.29437284814342, 25.933572974278015, 3),  # Чернівці
            ("Чернігів", 51.49938462501964, 31.28504327925128, 3),  # Чернігів
            ("Івано-Франківськ", 51.49938462501964, 31.28504327925128, 1),
            ("Севастополь", 44.61310722887907, 33.56472818800064, 10),
            ("Луганськ", 48.57407328231093, 39.29584885807574, 10)
        ]
        self.distances = []
        if exists("resources/distances.json"):
            print("Loading distances database using file 'distances.json'...")
            distances_file = open('resources/distances.json', 'r')
            self.distances = json.load(distances_file)
        else:
            print("Loading distances database using OpenStreetMaps API...")
            for city_from in self.cities:
                distances_from_city = []
                for city_to in self.cities:
                    if city_from != city_to:
                        distance = get_car_distance_between(city_from[2], city_from[1], city_to[2], city_to[1])
                        distances_from_city.append(distance)
                    else:
                        distances_from_city.append(0)
                print("From: {} Distances: {}".format(city_from[0], distances_from_city))
                self.distances.append(distances_from_city)
                with open("resources/distances.json", "w") as outfile:
                    outfile.write(json.dumps(self.distances))
        print("Loading has been completed...")

        self.setWindowTitle("Список міст")
        self.setMinimumSize(470, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.main_widget = QWidget()
        self.central_widget.addWidget(self.main_widget)

        layout = QVBoxLayout(self.main_widget)

        self.next_button = QPushButton("Маршрути")
        self.next_button.clicked.connect(self.path_form)
        layout.addWidget(self.next_button)

        self.table = QTableWidget(len(self.cities), 4)
        layout.addWidget(self.table)

        self.table.setHorizontalHeaderLabels(["Місто", "X", "Y", "Небезпечність"])
        self.table.setFixedHeight(500)

        self.add_row_button = QPushButton("Додати рядок")
        self.add_row_button.clicked.connect(self.add_row)
        layout.addWidget(self.add_row_button)

        self.save_button = QPushButton("Зберегти")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        for row in range(len(self.cities)):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsEditable)
            item.setText(self.cities[row][0])
            self.table.setItem(row, 0, item)
            X = QTableWidgetItem()
            X.setFlags(Qt.ItemFlag.ItemIsEditable)
            X.setText(str(self.cities[row][1]))
            self.table.setItem(row, 1, X)
            Y = QTableWidgetItem()
            Y.setFlags(Qt.ItemFlag.ItemIsEditable)
            Y.setText(str(self.cities[row][2]))
            self.table.setItem(row, 2, Y)
            Danger = QTableWidgetItem()
            Danger.setText(str(self.cities[row][3]))
            self.table.setItem(row, 3, Danger)

        layout.setAlignment(Qt.AlignTop)

        self.refresh_path_window_state()

        self.show()

    def add_row(self):
        self.table.insertRow(self.table.rowCount())

    def save_changes(self):
        for row in range(len(self.cities), self.table.rowCount()):
            lon_1 = self.table.item(row, 2).text()
            lat_1 = self.table.item(row, 1).text()

            distances_from_new_point = []
            for city_to in self.cities:
                distance_from = get_car_distance_between(lon_1, lat_1, city_to[2], city_to[1])
                # distance_to = get_car_distance_between(city_to[2], city_to[1], lon_1, lat_1)
                # self.distances[self.cities.index(city_to)].append(distance_to)
                self.distances[self.cities.index(city_to)].append(distance_from)
                distances_from_new_point.append(distance_from)
            distances_from_new_point.append(0)
            self.distances.append(distances_from_new_point)
            self.cities.append((str(self.table.item(row, 0).text()),
                                float(lat_1),
                                float(lon_1),
                                float(self.table.item(row, 3).text())))

        self.refresh_path_window_state()

    def calculate(self):
        evaluation_graph = []
        for i in range(len(self.cities)):
            evaluation_graph.append([0] * len(self.cities))
        # correct distances based on danger score through increasing distance to make city less attractable for ants
        for row in range(len(self.distances)):
            for col in range(len(self.distances[row])):
                distance = self.distances[row][col]
                danger_score = float(self.cities[row][3])
                evaluation_graph[row][col] = distance + (distance * (danger_score / 10))

        city_from = self.__city_search_index(self.path_widget.start_point_combobox.currentText())
        city_to = self.__city_search_index(self.path_widget.end_point_combobox.currentText())
        inner_points = self.path_widget.interPoints
        inner_cities = [self.__city_search_index(name) for name in inner_points]

        aco = AntColonyOptimizer(evaluation_graph, [city[3] for city in self.cities], 7, num_ants=100, num_iterations=1000)
        path = aco.run(city_from, city_to, inner_cities)
        self.show_calculated(path, self.__calculate_distance(path), self.__calculate_danger(path))

    def __city_search_index(self, name):
        for index in range(len(self.cities)):
            if self.cities[index][0] == name:
                return index

    def __calculate_distance(self, path):
        total_distance = 0
        for index in range(len(path)):
            if index != len(path) - 1:
                node = path[index]
                total_distance += self.distances[node][path[index + 1]]
        return total_distance

    def __calculate_danger(self, path):
        total_danger = 0
        for city in path[1:]:
            total_danger += self.cities[city][3]
        return total_danger / (len(path) - 1)

    def path_form(self):
        self.central_widget.setCurrentWidget(self.path_widget)

    def show_main_window(self):
        self.central_widget.setCurrentWidget(self.main_widget)

    def show_calculated(self, path, distance, danger_score):
        cities_names = []
        for node in path:
            cities_names.append(self.cities[node][0])
        msg = "Calculation Results:\nPath: {} \nDistance(in kilometers): {}\nDanger Score: {}".format('->'.join(cities_names),
                                                                                       round((distance/1000),2), danger_score)
        self.path_widget.layout().insertWidget(self.path_widget.layout().count(), QLabel(msg))

        labels_layout = QHBoxLayout()
        green_label = QLabel("Зелений - безпечно")
        green_label.setStyleSheet("color: green")
        yellow_label = QLabel("Жовтий - умовно безпечно")
        yellow_label.setStyleSheet("color: orange")
        red_label = QLabel("Червоний - небезпечно")
        red_label.setStyleSheet("color: red")
        labels_layout.addWidget(green_label)
        labels_layout.addWidget(yellow_label)
        labels_layout.addWidget(red_label)
        self.path_widget.layout().insertLayout(self.path_widget.layout().count(), labels_layout)

        table = QTableWidget(1, 10)
        for i in reversed(range(int(danger_score))):
            table.setColumnWidth(i, 10)
            color = "green"
            if 0 <= i <= 3:
                color = "green"
            elif 3 < i <= 7:
                color = "yellow"
            else:
                color = "red"
            item = QTableWidgetItem()
            item.setBackground(QColor(color))
            table.setItem(0, i, item)

        self.path_widget.layout().insertWidget(self.path_widget.layout().count(), table)

    def refresh_path_window_state(self):
        self.path_widget = PathWindow(self.cities)
        self.central_widget.addWidget(self.path_widget)
        self.path_widget.back_button.clicked.connect(self.show_main_window)
        self.path_widget.calculate_button.clicked.connect(self.calculate)


class PathWindow(QWidget):
    def __init__(self, Cities):
        super().__init__()

        self.comboBoxes = []

        self.interPoints = []

        self.setWindowTitle("Вибір точок")

        self.nameCities = []

        for city in Cities:
            self.nameCities.append(city[0])

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.back_button = QPushButton("Точки призначень")
        layout.addWidget(self.back_button)

        self.calculate_button = QPushButton("Розрахувати")
        layout.addWidget(self.calculate_button)

        self.start_point_label = QLabel("Початкова точка:")
        layout.addWidget(self.start_point_label)

        self.start_point_combobox = QComboBox()
        self.start_point_combobox.addItems(self.nameCities)
        layout.addWidget(self.start_point_combobox)

        self.end_point_label = QLabel("Кінцева точка:")
        layout.addWidget(self.end_point_label)

        self.end_point_combobox = QComboBox()
        self.end_point_combobox.addItems(self.nameCities)
        layout.addWidget(self.end_point_combobox)
        self.add_point_button = QPushButton("Додати точку")
        self.add_point_button.clicked.connect(self.add_intermediate_point)
        layout.addWidget(self.add_point_button)
        self.intermediate_point_label = QLabel("Проміжна точка:")
        layout.addWidget(self.intermediate_point_label)

        self.setLayout(layout)

    def add_intermediate_point(self):
        intermediate_point_combobox = QComboBox()
        intermediate_point_combobox.addItems(self.nameCities)
        intermediate_point_combobox.currentIndexChanged.connect(self.combobox_changed)
        self.comboBoxes.append(intermediate_point_combobox)
        self.layout().insertWidget(self.layout().count(), intermediate_point_combobox)
        self.interPoints.append(intermediate_point_combobox.currentText())

    def combobox_changed(self, index):
        self.interPoints.clear()
        for box in self.comboBoxes:
            self.interPoints.append(box.currentText())


if __name__ == "__main__":
    app = QApplication([])
    window = CityNamesWindow()
    window.show()
    app.exec()
