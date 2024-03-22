import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QFormLayout, QHeaderView,
                               QHBoxLayout, QLineEdit, QMainWindow,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QLabel, QMessageBox)
from PySide6.QtCharts import QChartView, QLineSeries, QChart

import ast
import operator as op

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

'''
    The Aplication will have a main window
        At the top will be a input field to write the function to plot
        At the bottom will be two inputs, one for the minimum value and the other for the maximum value
        
        Then there will be a button to plot the function or delete the plot
        
        The plot will be shown in the middle of the window
'''

def eval_(node):
    match node:
        case ast.Constant(value) if isinstance(value, int):
            return value  # integer
        case ast.BinOp(left, op, right):
            return operators[type(op)](eval_(left), eval_(right))
        case ast.UnaryOp(op, operand):  # e.g., -1
            return operators[type(op)](eval_(operand))
        case _:
            raise TypeError(node)

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # Top
        
        self.function_layout = QHBoxLayout()
        
        self.function_label = QLabel("Function:")
        self.function_layout.addWidget(self.function_label)
        
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("x^2")
        self.function_layout.addWidget(self.function_input)

        self.layout.addLayout(self.function_layout)

        # Middle
        self.range_layout = QHBoxLayout()
        
        self.min_label = QLabel("Limite Inferior:")
        self.range_layout.addWidget(self.min_label)
        
        self.min_input = QLineEdit()
        self.min_input.setPlaceholderText("0")
        self.range_layout.addWidget(self.min_input)
        
        self.max_label = QLabel("Limite Superior:")
        self.range_layout.addWidget(self.max_label)

        self.max_input = QLineEdit()
        self.max_input.setPlaceholderText("10")
        self.range_layout.addWidget(self.max_input)

        self.layout.addLayout(self.range_layout)
        
        # Bottom
        self.buttons_layout = QHBoxLayout()

        self.plot_button = QPushButton("Graficar")
        self.plot_button.clicked.connect(self.plot)
        self.buttons_layout.addWidget(self.plot_button)
        
        self.delete_button = QPushButton("Borrar")
        self.delete_button.clicked.connect(self.delete)
        self.buttons_layout.addWidget(self.delete_button)
        
        self.layout.addLayout(self.buttons_layout)

        # Plot
        self.chart = QChart()
        self.chart.setTitle("Función")

        ## Set minimum height for the chart
        self.chart.setMinimumHeight(400)
        
        self.layout.addWidget(QChartView(self.chart))
        
        self.setLayout(self.layout)

    @Slot()
    def plot(self):
        # Prevent empty inputs
        if self.function_input.text() == "" or self.min_input.text() == "" or self.max_input.text() == "":
            QMessageBox.critical(self, "Error", "Por favor, llene todos los campos")
            return
        
        # Remove previous series
        self.delete()
        
        # Get the min and max values
        min_value = float(self.min_input.text())
        max_value = float(self.max_input.text())
        
        # Get the function
        function = self.function_input.text()
        
        # Create the series
        series = QLineSeries()

        # Add the points to the series
        for x in range(int(min_value), int(max_value) + 1):
            
            # Replace the x value in the function
            # y = eval(function.replace("x", str(x)))
            
            exp_to_eval = function.replace("x", str(x))
            try:
                y = eval_(ast.parse(exp_to_eval, mode='eval').body)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al evaluar la función: {e}")
                return
            
            print(f"f({x}): {exp_to_eval} = {y}")
            
            series.append(x, y)
            
        # Add the series to the chart
        
        self.chart.addSeries(series)
        
        # Set the axes
        self.chart.createDefaultAxes()
        
        # Set the title
        self.chart.setTitle("Función: " + function)        
        
    @Slot()
    def delete(self):
        # Clear the chart
        self.chart.removeAllSeries()  
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graficador de Funciones")
        # self.setGeometry(100, 100, 800, 600)

        self.widget = Widget()
        self.setCentralWidget(self.widget)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())