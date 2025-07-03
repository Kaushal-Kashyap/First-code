
import random

def spin_row() :
    symbols = ["🍒", "🍉", "🍋", "🔔", "⭐"]
    return [random.choice(symbols) for _ in range(3)]

def print_row(row):
    print("*" * 20)
    print("|".join(row))
    print("*" * 20)

def get_payout(row,bet):
    if row[0] == row[1] == row[2] :
        if row[0] == "🍒":
            return bet * 4
        elif row[0] == "🍉":
            return bet * 6
        elif row[0] == "🍋":
            return bet * 8
        elif row[0] == "🔔":
            return bet * 12
        elif row[0] == "⭐":
            return bet * 20
    # Check for two matching symbols (partial match)
    if row[0] == row[1] or row[1] == row[2] :
        if "🍒" in row:
            return bet * 1.2
        elif "🍉" in row:
            return bet * 1.5
        elif "🍋" in row:
            return bet * 1.8
        # elif "🔔" in row:
        #     return bet * 3
        # elif "⭐" in row:
        #     return bet * 3.5
    return 0
            

def main():
    balance = 1000

    print("*****************************")
    print("Welcome to the Slot Machine")
    print("Symbols: 🍒 🍉 🍋 🔔 ⭐")
    print("*****************************")

    while balance > 0:
        print(f"Your current balance is: ${balance}")
        bet = input("Enter your bet : ")

        if not bet.isdigit() :
            print("Enter a valid number")
            continue

        bet = int(bet)
        if bet > balance :
            print("Isufficient balance")
        elif bet <= 0:
            print("bet must be greater than 0")
            continue

        balance -= bet

        row = spin_row()
        print("Spinning...")
        print_row(row)
        if balance == 0:
            print("Insufficeint balance")
            break
        
        payout = get_payout(row,bet)
        if payout == 0 :
            print("You Lose")
        else:
            print(f"You win: {payout}")
            balance += payout
    
        if not input("Play Again? (Yes or No): ").lower() == "yes" :
            print("Thanks for Playing")
            break
        print("*****************************")
if __name__ == "__main__":
    main()