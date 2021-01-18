import random
import sqlite3
import time

random.seed(time.time())
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
);""")
conn.commit()

class BankingSystem:

    @staticmethod
    def menu():
        while True:
            print('''
1. Create an account
2. Log into account
0. Exit''')
            user_choice = int(input())
            if user_choice == 1:
                BankingSystem.create()
            elif user_choice == 2:
                BankingSystem.log_in()
            elif user_choice == 0:
                print("Bye!")
                exit()

    @staticmethod
    def create():
        acc = "400000"
        for _ in range(9):
            acc += str(random.randint(0, 9))
        number = acc
        check_sum = 0
        for i in range(15):
            digit = int(number[i])
            if not i % 2:
                digit *= 2
            if digit >= 10:
                digit -= 9
            check_sum += digit
        last_number = ((check_sum // 10 + 1) * 10 - check_sum) % 10
        number += str(last_number)
        password = str()
        for _ in range(4):
            password += str(random.randint(0, 9))
        cur.execute(f"""INSERT INTO card (number, pin) VALUES ({number}, {str(password)})""")
        conn.commit()
        print(f'''Your card has been created
Your card number:
{number}
Your card PIN:
{password}\n''')

    @staticmethod
    def log_in():
        card = input('Enter your card number:\n')
        pin = input('Enter your PIN:\n')
        cur.execute(f"""SELECT number, pin, balance FROM card WHERE number={card} AND pin={pin}""")
        data = cur.fetchall()
        try:
            if data:
                print('You have successfully logged in!\n')
                BankingSystem.log_in_menu(card)
            else:
                print('Wrong card number or PIN!\n')
        except IndexError:
            print('Wrong card number or PIN!\n')

    @staticmethod
    def log_in_menu(card):
        while True:
            print('''1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit''')
            cur.execute(f"""SELECT number, pin, balance FROM card WHERE number={card}""")
            data = cur.fetchall()
            user_input = int(input())
            if user_input == 1:
                print(f'Balance: {data[0][2]}')
            elif user_input == 2:
                BankingSystem.adding(card, data[0][2])
            elif user_input == 3:
                BankingSystem.transfer(card, data[0][2])
            elif user_input == 4:
                BankingSystem.close(card)
            elif user_input == 5:
                print('You have successfully logged out!')
                break
            elif user_input == 0:
                exit()

    @staticmethod
    def adding(number, bal):
        print('Enter income:')
        sum = int(input())
        print('Income was added!')
        cur.execute(f"""UPDATE card
SET balance = {bal + sum}
WHERE number = {number};""")
        conn.commit()

    @staticmethod
    def transfer(card, balance):
        print('''Transfer
Enter card number:''')
        transfer_card = input()
        if transfer_card == card:
            print("You can't transfer money to the same account!")
        elif int(transfer_card[0]) != 4:
            print('Such a card does not exist.')
        elif BankingSystem.luhn(transfer_card):
            cur.execute(f"""SELECT number, balance FROM card WHERE number={transfer_card}""")
            inport_data = cur.fetchall()
            try:
                if inport_data:
                    print('Enter how much money you want to transfer:')
                    money = int(input())
                    if money > balance:
                        print('Not enough money!\n')
                    else:
                        cur.execute(f"""UPDATE card
    SET balance = {balance - money}
    WHERE number = {card};""")
                        cur.execute(f"""UPDATE card
    SET balance = {inport_data[0][1] + money}
    WHERE number = {transfer_card};""")
                        conn.commit()
                        print('Success!\n')
            except IndexError:
                print('Such a card does not exist.')
        else:
            print('Probably you made a mistake in the card number. Please try again!\n')

    @staticmethod
    def luhn(card):
        check_sum = 0
        for i in range(16):
            digit = int(card[i])
            if not i % 2:
                digit *= 2
            if digit >= 10:
                digit -= 9
            check_sum += digit
        return (check_sum % 10) == 0

    @staticmethod
    def close(card):
        cur.execute(f"""DELETE FROM card WHERE number={card}""")
        conn.commit()
        print('The account has been closed!')


BankingSystem.menu()
conn.close()


