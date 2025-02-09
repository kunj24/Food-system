from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QListWidget, QWidget, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import sys
import sqlite3

# Database Setup
conn = sqlite3.connect("food_orders.db")
cursor = conn.cursor()

# Create orders table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        items TEXT,
        total_bill REAL
    )
""")
conn.commit()

# Food Menu Dictionary
menu = {
    "Pizza": (10, "Fast Food"),
    "Burger": (5, "Fast Food"),
    "Pasta": (8, "Italian"),
    "Sushi": (12, "Japanese"),
    "Tacos": (7, "Mexican"),
    "Biryani": (9, "Indian"),
    "Salad": (6, "Healthy"),
    "Ice Cream": (4, "Dessert")
}

# Set to Store Unique Customers
unique_customers = set()

class FoodDeliverySystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Food Delivery System")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon("food_icon.png"))
        self.init_ui()

    def init_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel("Online Food Delivery System")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Customer Name Input
        name_layout = QHBoxLayout()
        name_label = QLabel("Customer Name: ")
        name_label.setFont(QFont("Arial", 14))
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 12))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Menu Selection
        item_layout = QHBoxLayout()
        item_label = QLabel("Select Item: ")
        item_label.setFont(QFont("Arial", 14))
        self.item_combo = QComboBox()
        self.item_combo.addItems(menu.keys())
        self.item_combo.setFont(QFont("Arial", 12))
        add_button = QPushButton("Add to Order")
        add_button.setFont(QFont("Arial", 12))
        add_button.clicked.connect(self.add_item_to_order)
        item_layout.addWidget(item_label)
        item_layout.addWidget(self.item_combo)
        item_layout.addWidget(add_button)
        main_layout.addLayout(item_layout)

        # Order List
        self.order_list = QListWidget()
        self.order_list.setFont(QFont("Courier", 12))
        main_layout.addWidget(self.order_list)

        # Total Bill Display
        self.total_bill_label = QLabel("Total Bill: $0")
        self.total_bill_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(self.total_bill_label)

        # Place Order & Generate Bill Buttons
        button_layout = QHBoxLayout()

        place_order_button = QPushButton("Place Order")
        place_order_button.setFont(QFont("Arial", 14))
        place_order_button.clicked.connect(self.place_order)

        generate_bill_button = QPushButton("Generate Bill")
        generate_bill_button.setFont(QFont("Arial", 14))
        generate_bill_button.clicked.connect(self.generate_bill)

        button_layout.addWidget(place_order_button)
        button_layout.addWidget(generate_bill_button)
        main_layout.addLayout(button_layout)

        # Revenue & Customers Summary
        summary_layout = QHBoxLayout()
        revenue_button = QPushButton("Show Total Revenue")
        revenue_button.setFont(QFont("Arial", 12))
        revenue_button.clicked.connect(self.show_revenue)

        customers_button = QPushButton("Show Unique Customers")
        customers_button.setFont(QFont("Arial", 12))
        customers_button.clicked.connect(self.show_unique_customers)

        summary_layout.addWidget(revenue_button)
        summary_layout.addWidget(customers_button)
        main_layout.addLayout(summary_layout)

        # Summary Label
        self.summary_label = QLabel("")
        self.summary_label.setFont(QFont("Arial", 12))
        self.summary_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.summary_label)

        central_widget.setLayout(main_layout)

        # Order Storage
        self.current_order = []
        self.total_bill = 0

    def add_item_to_order(self):
        item = self.item_combo.currentText()
        price, category = menu[item]
        self.current_order.append((item, price, category))
        self.order_list.addItem(f"{item} - ${price} ({category})")
        self.total_bill += price
        self.total_bill_label.setText(f"Total Bill: ${self.total_bill}")

    def place_order(self):
        customer_name = self.name_input.text().strip()
        if not customer_name:
            QMessageBox.warning(self, "Error", "Customer name cannot be empty!")
            return
        if not self.current_order:
            QMessageBox.warning(self, "Error", "Order list is empty!")
            return

        item_names = ", ".join([item[0] for item in self.current_order])

        # Store in database
        cursor.execute("INSERT INTO orders (customer_name, items, total_bill) VALUES (?, ?, ?)",
                       (customer_name, item_names, self.total_bill))
        conn.commit()

        # Add to unique customer set
        unique_customers.add(customer_name)

        QMessageBox.information(self, "Success", f"Order placed successfully for {customer_name}!\nTotal: ${self.total_bill}")

        # Reset order
        self.current_order.clear()
        self.order_list.clear()
        self.total_bill = 0
        self.total_bill_label.setText("Total Bill: $0")

    def generate_bill(self):
        customer_name = self.name_input.text().strip()
        if not customer_name or not self.current_order:
            QMessageBox.warning(self, "Error", "No order to generate bill!")
            return

        bill_text = f"** Invoice **\nCustomer: {customer_name}\n\nItems Ordered:\n"
        for item, price, category in self.current_order:
            bill_text += f"- {item} (${price}) - {category}\n"

        bill_text += f"\nTotal Amount: ${self.total_bill}"

        QMessageBox.information(self, "Generated Bill", bill_text)

    def show_revenue(self):
        cursor.execute("SELECT SUM(total_bill) FROM orders")
        total_revenue = cursor.fetchone()[0]
        total_revenue = total_revenue if total_revenue else 0
        QMessageBox.information(self, "Total Revenue", f"Total Revenue Generated: ${total_revenue}")

    def show_unique_customers(self):
        cursor.execute("SELECT DISTINCT customer_name FROM orders")
        customers = cursor.fetchall()
        customer_list = [customer[0] for customer in customers]

        if customer_list:
            QMessageBox.information(self, "Unique Customers",
                                    "Customers who have placed orders:\n" + "\n".join(customer_list))
        else:
            QMessageBox.information(self, "Unique Customers", "No customers have placed an order yet.")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FoodDeliverySystem()
    window.show()
    sys.exit(app.exec_())
