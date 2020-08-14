from random import randint
import sqlite3

connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()

# database variables
CREATE_CARD_TABLE = """CREATE TABLE IF NOT EXISTS card( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                                        number TEXT,
                                                        pin TEXT,
                                                        balance INTEGER DEFAULT 0
                                                        );"""
INSERT_INTO_CARD = "INSERT INTO card (number, pin) VALUES (?, ?)"
GET_BALANCE_FROM_ = "SELECT balance FROM card WHERE number = (?)"
UPDATE_BALANCE_FROM_ = "UPDATE card SET balance = balance + (?) WHERE number = (?)"
GET_NUMBERS_ONLY = "SELECT number FROM card;"
GET_PIN_FROM_ = "SELECT pin FROM card WHERE number = (?)"
GET_NUMBER_FROM_ = "SELECT number FROM card WHERE number = (?)"
DELETE_ACCOUNT_FROM_ = "DELETE FROM card WHERE number = (?)"

cursor.execute(CREATE_CARD_TABLE)
connection.commit()

# DROP TABLE
# cursor.execute("DROP TABLE card")
# connection.commit()

# DELETE TABLE content
# cursor.execute("DELETE FROM card")
# connection.commit()


class BankAccount:
    accounts = {}
    cards_issued = set()

    def __init__(self):
        self.account = new_card()
        self.pin = ''.join([str(randint(0, 9)) for x in range(4)])
        self.balance = 0

        while self.account not in BankAccount.cards_issued:
            BankAccount.accounts.update({self.account: {'pin': self.pin, 'balance': self.balance}})
            BankAccount.cards_issued.add(self.account)
            # add new account to database
            cursor.execute(INSERT_INTO_CARD, (self.account, self.pin))
            connection.commit()


def new_card():
    number = [4, 0, 0, 0, 0, 0] + [randint(0, 9) for x in range(9)]
    every_2nd = [str(x) if i % 2 != 0 else str(x * 2) for i, x in enumerate(number)]
    sum_digits = [int(x) for x in [str(int(x[0]) + int(x[1])) if len(x) == 2 else x for i, x in enumerate(every_2nd)]]
    return ''.join([str(x) for x in number + [(sum(sum_digits) * 9) % 10]])


def luhn_check_calculator(check_input):
    every_2nd = [x * 2 if i % 2 == 0 else x for i, x in enumerate([int(x) for x in check_input])]
    sum_double_digit = [(x - 9) if x > 9 else x for x in every_2nd]
    return sum(sum_double_digit) % 10


keep_looping = True
while keep_looping:
    user_input_1 = input('1. Create an account\n2. Log into account\n0. Exit\n> ')

    # Exit:
    if user_input_1 == '0':
        keep_looping = False

    # Create an account:
    elif user_input_1 == '1':
        new = BankAccount()
        print(f'\nYour card has been created\nYour card number:\n{new.account}\nYour card PIN:\n{new.pin}\n')

    # Log into account:
    elif user_input_1 == '2':
        login, password = input('\nEnter your card number:\n> '), input('Enter your PIN:\n> ')

        check_number = cursor.execute(GET_NUMBERS_ONLY).fetchall()
        check_pin = cursor.execute(GET_PIN_FROM_, (login,))

        if (login,) in check_number and (password,) in check_pin:
            print('\nYou have successfully logged in!\n')

            while True:
                sub_menu = '1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n> '
                user_input_2 = input(sub_menu)

                # Exit:
                if user_input_2 == '0':
                    keep_looping = False
                    break

                # Balance:
                elif user_input_2 == '1':
                    get_balance = cursor.execute(GET_BALANCE_FROM_, (login,)).fetchone()
                    print(f'\nBalance: {"".join(map(str, get_balance))}\n')

                # Add income:
                elif user_input_2 == '2':
                    add_income = abs(int(input('\nEnter income:\n> ')))
                    cursor.execute(UPDATE_BALANCE_FROM_, (add_income, login))
                    connection.commit()
                    print('Income was added!\n')

                # Do transfer:
                elif user_input_2 == '3':
                    transfer_input = input('\nTransfer\nEnter card number:\n> ')
                    like = cursor.execute(GET_NUMBER_FROM_, (transfer_input,)).fetchone()
                    # 1st check for proper card
                    if luhn_check_calculator(transfer_input) != 0:
                        print('Probably you made mistake in card number. Please try again!\n')
                    else:
                        # 2nd check if is in database
                        if like is not None:

                            transfer_money = abs(int(input('Enter how much money you want to transfer:\n> ')))
                            get_balance = cursor.execute(GET_BALANCE_FROM_, (login,)).fetchone()
                            # 3th check if enough balance
                            if (transfer_money,) <= get_balance:
                                cursor.execute(UPDATE_BALANCE_FROM_, ((transfer_money * -1), login))
                                connection.commit()
                                cursor.execute(UPDATE_BALANCE_FROM_, (transfer_money, transfer_input))
                                connection.commit()
                                print('Success!\n')
                            else:
                                print('Not enough money!\n')
                        else:
                            print('Such a card does not exist.\n')

                # Close account:
                elif user_input_2 == '4':
                    cursor.execute(DELETE_ACCOUNT_FROM_, (login,))
                    connection.commit()
                    print('\nThe account has been closed!\n')

                # Log out:
                elif user_input_2 == '5':
                    print('\nYou have successfully logged out!\n')
                    break

        else:
            print('\nWrong card number or PIN!\n')

print('\nBye!')
connection.close()
