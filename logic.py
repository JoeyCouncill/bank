from PyQt6.QtWidgets import *
from gui import *
import csv


class Logic(QMainWindow, Ui_Dialog):
    """Handles all the logic for the gui as well as for the banking
    Attributes:
        __account_name (str): The name of the active account
        """
    INTEREST_RATE = 1.02

    def __init__(self):
        """Initializes the logic class and invokes methods as needed"""
        super().__init__()
        self.setupUi(self)
        self.__account_name: str = ''

        self.log_in_button.clicked.connect(lambda: self.log_in())
        self.sign_up_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.sign_up_page))
        self.go_back_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.log_in_page))
        self.sign_up_button_2.clicked.connect(lambda: self.sign_up())
        self.account_select_box.currentIndexChanged.connect(lambda: self.switch_account())
        self.continue_button.clicked.connect(lambda: self.transaction())

    def log_in(self):
        """Controls the functions of the login page"""
        name: str = self.name_line.text()
        password: str = self.password_line.text()
        try:
            if name and password != '':
                for names, passwords in self.login_read().items():
                    if names == name and passwords == password:
                        self.set_name(name)
                        self.set_password(password)
                        self.pages.setCurrentWidget(self.landing_page)
                        self.switch_account()
                        return
                raise AccountException
            else:
                raise MissingValuesException
        except AccountException:
            self.log_in_error_label.setText("No account found with given name and password, please try again or sign up.")
        except MissingValuesException:
            self.log_in_error_label.setText("Please enter a user name and password.")

    def switch_account(self):
        """Switches which account is currently being accessed by the user"""
        self.account_label.setText(self.account_select_box.currentText())
        self.balance_line.setText(self.get_balance()[self.account_select_box.currentIndex() + 1])

    def sign_up(self):
        """controls the functions of the signup page"""
        name: str = self.name_sign_up_line.text()
        password: str = self.password_sign_up_line.text()
        try:
            if name and password != '':
                for names in self.login_read():
                    if names == name:
                        raise AccountException
            else:
                raise MissingValuesException
        except AccountException:
            self.sign_up_error_label.setText("An account with this name already exists, try logging in.")
        except MissingValuesException:
            self.sign_up_error_label.setText("Please enter a user name and password.")
        else:
            self.login_write(name, password)
            self.set_name(name)
            self.account_write()
            self.pages.setCurrentWidget(self.landing_page)
            self.switch_account()

    def transaction(self):
        """controls all transactions"""
        self.landing_page_error_box.setText('')
        try:
            account: int = self.account_select_box.currentIndex()
            amount: float = float(self.amount_line.text())
            transaction_type: int = self.action_type_box.currentIndex()
            balance: list = self.get_balance()
            interest: int = int(balance[3])
            if transaction_type == 0:
                new_balance: str = str(round((float(balance[account + 1]) + amount), 2))
                if account == 1:
                    interest: str = str(interest + 1)
                    if int(interest) % 5 == 0:
                        new_balance: str = str(round(self.apply_interest(float(new_balance)), 2))
            elif transaction_type == 1:
                new_balance: str = str(round((float(balance[account + 1]) - amount), 2))
                if float(new_balance) < 0:
                    raise BalanceException
            if account == 0:
                new: list = [self.__account_name, new_balance, balance[2], interest]
            elif account == 1:
                new: list = [self.__account_name, balance[1], new_balance, interest]

            with open('accounts.csv', 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')
                lists: list = [list(rows) for rows in csv_reader]
                newlist: list = []
                for data in lists:
                    if data[0] == self.__account_name:
                        data: list = new
                    newlist.append(data)
            with open('accounts.csv', 'w', newline='') as writer:
                csv_writer = csv.writer(writer)
                csv_writer.writerows(newlist)
            self.balance_line.setText(self.get_balance()[self.account_select_box.currentIndex() + 1])
        except ValueError:
            self.landing_page_error_box.setText('Please enter only numbers')
        except BalanceException:
            self.landing_page_error_box.setText('Not enough funds available for transaction')

    def apply_interest(self, balance: float):
        """applies interest to the users savings account every fifth transaction
        :param balance: (float): a float of the users current savings account balance
        :return: balance with interest applied
        """
        balance *= self.INTEREST_RATE
        return balance

    def login_read(self):
        """Accesses the login.csv file containing usernames and passwords for all accounts.
         It then converts this data into a dictionary
         :return: a dictionary of account usernames and passwords"""
        with open('login.csv', 'r') as in_file:
            csv_reader = csv.reader(in_file, delimiter=',')
            dictionary: dict = {rows[0]: rows[1] for rows in csv_reader}
        return dictionary

    def login_write(self, name: str, password: str):
        """writes a new accounts username and password to the login.csv file
        :param name (str) entered name of account
        :param password (str) entered password of account"""
        with open('login.csv', 'a', newline='') as csvfile:
            content = csv.writer(csvfile)
            content.writerow((name, password))

    def get_balance(self):
        """accesses the accounts.csv file containing account balances and
         the number of savings transactions for all accounts
         :return: A list of accounts and their balances"""
        with open('accounts.csv', 'r') as in_file:
            csv_reader = csv.reader(in_file, delimiter=',')
            for rows in csv_reader:
                if rows[0] == self.__account_name:
                    return list(rows)

    def account_write(self):
        """Writes a new accounts name and account balances
        (zero for both accounts) to the accounts.csv file"""
        with open('accounts.csv', 'a', newline='') as csvfile:
            content = csv.writer(csvfile)
            content.writerow([self.__account_name, 0, 0, 0])

    def set_name(self, value):
        """passes the active users name to the class"""
        self.__account_name: str = value


class AccountException(Exception):
    """Exception to be raised when no account with given username and
    password are found or when an account already exists with a given name"""
    pass


class MissingValuesException(Exception):
    """Exception to be raised when the application does not
    receive both a username and password upon login or sign up """
    pass


class BalanceException(Exception):
    """Exception to be raised when an account has been attempted to be overdrawn"""
    pass
