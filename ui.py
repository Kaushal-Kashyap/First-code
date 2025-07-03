
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,QLineEdit
from PyQt5.QtCore import QTimer
from test import get_payout

class SlotMachine(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Slot Machine")
        self.setFixedSize(350, 300)

        # Symbols (can be emojis, text, or image paths)
        self.symbols = ['🍒', '🍋', '🔔', '🍉', '⭐']

        # Game state
        self.starting_balance = 1000
        self.balance = self.starting_balance
        self.spin_count = 0
        self.total_wins = 0
        self.total_losses = 0

        # Layouts
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Balance display
        self.balance_label = QLabel(f"Balance: ${self.balance}", self)
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(self.balance_label)

        # Stats display
        self.stats_label = QLabel(self)
        self.stats_label.setStyleSheet("font-size: 14px; color: #555;")
        self.update_stats()
        main_layout.addWidget(self.stats_label)

        # Bet input
        bet_layout = QHBoxLayout()
        bet_label = QLabel("Bet:", self)
        bet_label.setStyleSheet("font-size: 16px;")
        self.bet_input = QLineEdit(self)
        self.bet_input.setPlaceholderText("Enter bet amount")
        self.bet_input.setFixedWidth(150)
        bet_layout.addWidget(bet_label)
        bet_layout.addWidget(self.bet_input)
        main_layout.addLayout(bet_layout)

        # Slot symbols
        self.slots_layout = QHBoxLayout()
        self.labels = [QLabel("❔", self) for _ in range(3)]
        for label in self.labels:
            label.setStyleSheet("font-size: 40px;")
            self.slots_layout.addWidget(label)
        main_layout.addLayout(self.slots_layout)


        # Spin and Reset buttons
        button_layout = QHBoxLayout()
        self.button = QPushButton("Spin")
        self.button.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.button.clicked.connect(self.start_spin)
        button_layout.addWidget(self.button)

        self.reset_button = QPushButton("Reset Game")
        self.reset_button.setStyleSheet("font-size: 14px;")
        self.reset_button.clicked.connect(self.reset_game)
        button_layout.addWidget(self.reset_button)
        main_layout.addLayout(button_layout)


        # Last spin result label
        self.last_spin_label = QLabel("", self)
        self.last_spin_label.setStyleSheet("font-size: 18px; color: #333;")
        main_layout.addWidget(self.last_spin_label)

        # Message label
        self.message_label = QLabel("", self)
        self.message_label.setStyleSheet("font-size: 16px; color: green;")
        main_layout.addWidget(self.message_label)

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_symbols)
        self.duration_timer = QTimer()
        self.duration_timer.setSingleShot(True)
        self.duration_timer.timeout.connect(self.stop_spin)

    def start_spin(self):
        bet_text = self.bet_input.text()
        if not bet_text.isdigit():
            self.message_label.setText("Enter a valid bet amount.")
            return
        bet = int(bet_text)
        if bet <= 0:
            self.message_label.setText("Bet must be greater than 0.")
            return
        if bet > self.balance:
            self.message_label.setText("Insufficient balance.")
            return
        self.bet = bet
        self.balance -= bet
        self.update_balance()
        self.message_label.setText("")
        self.button.setDisabled(True)
        self.bet_input.setDisabled(True)
        self.timer.start(100)  # update every 100ms
        self.duration_timer.start(1500)  # run for 1.5 seconds

        # Clear last spin result
        self.last_spin_label.setText("")

    def update_symbols(self):
        for label in self.labels:
            label.setText(random.choice(self.symbols))

    def stop_spin(self):
        self.timer.stop()
        # Final slot result
        result = [random.choice(self.symbols) for _ in range(3)]
        for i, label in enumerate(self.labels):
            label.setText(result[i])
        # Calculate payout using get_payout from test.py
        payout = get_payout(result, self.bet)
        if payout > 0:
            self.message_label.setStyleSheet("font-size: 16px; color: green;")
            self.message_label.setText(f"You win: ${payout}")
            self.balance += payout
        else:
            self.message_label.setStyleSheet("font-size: 16px; color: red;")
            self.message_label.setText("You lose!")
        self.update_balance()
        self.button.setDisabled(False)
        self.bet_input.setDisabled(False)
        if self.balance <= 0:
            self.message_label.setText("Game Over! No balance left.")
            self.button.setDisabled(True)
            self.bet_input.setDisabled(True)

    def update_balance(self):
        self.balance_label.setText(f"Balance: ${self.balance}")

# Run the App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SlotMachine()
    window.show()
    sys.exit(app.exec_())
