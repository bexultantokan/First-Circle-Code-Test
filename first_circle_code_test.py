import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import bcrypt

cred = credentials.Certificate("Firebase_Admin_credentials.json") # path to the credentials file for the Firebase 
firebase_admin.initialize_app(cred)

db = firestore.client()

def name_request(message): # a reusable function to request a name from the user
    print(message)
    name = input().strip()
    if name.isalpha():
        return name
    else:
        print("Please type a valid string")
        return name_request()
    
def birth_year_request():   # function to request a birth year from the user            
    print("Please type your birth year:")
    birth_year = input().strip()
    if len(birth_year) == 4 and birth_year.isnumeric() and int(birth_year) <= 2024:
        return int(birth_year)
    else:
        print("Please type a valid year")
        return birth_year_request()
    
def if_exists(login): # function to check if the user with the given login already exists
    doc_ref = db.collection('users').document(login) # lazy load, makes only one request, does not load the whole collection 
    doc = doc_ref.get()
    return True if doc.exists else False

def login_request(): # function to request a login from the user
    print('Please enter your account login:')
    login = input().strip().lower()
    if if_exists(login):
        print('This username already exists. Please choose another one')
        return login_request()
    else:
        return login
    
def password_request(): # function to request a password from the user. The password is hashed with bcrypt
    print('Please enter your account password (minimum 6 char long):')
    password = input().strip()
    if len(password) < 6:
        print('Password is too short. Please enter a password with minimum 6 characters')
        return password_request()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print("Username successfully created!")
    return hashed_password

def number_request(message):    # a reusable function to request a number from the user
    print(message)
    deposit = input().strip()
    try:
        deposit = int(deposit) 
        if deposit < 0:
            print("Please type a valid positive number")
            return number_request(message)
    except ValueError:
        print("Please type a valid number")
        return number_request(message)
    return int(deposit)

def open_account(): # function to open an account
    first_name = name_request("Please type your first name:")
    last_name = name_request("Please type your last name:")
    birth_year = birth_year_request()
    login = login_request()
    hashed_password = password_request()
    initial_deposit = number_request("Please enter the amount of your initial deposit:")
    doc_ref = db.collection("users").document(login)
    
    doc_ref.set({"first": first_name, "last": last_name, "born": birth_year, "login": login, "hashed_password": hashed_password, "balance": initial_deposit})
    
    print("Your account is successfully created!")
    print("Please remember your account number for further sign in")
    logged_in_menu(login, doc_ref, first_name, last_name)

def sign_in():  # function to sign in to the account
    print("Please enter login or press 9 to exit")
    login = input().strip().lower()
    if login == '9':
        return
    print("Please enter password")
    
    password = input().strip() 
    doc_ref = db.collection("users").document(login)
    if doc_ref.get().exists:
        doc = doc_ref.get().to_dict()
        if bcrypt.checkpw(password.encode('utf-8'), doc["hashed_password"]):
            print("You are successfully signed in!")
            logged_in_menu(login, doc_ref, doc['first'], doc['last'])
        else:
            print("Wrong login or password")
            return sign_in()  
    else:
        print("Wrong login or password")
        return sign_in()  

def check_balance(doc_ref): # function to check the balance of the account
    try:
        balance = doc_ref.get().to_dict()['balance']
    except:
        print("There was an error while checking the balance")
    print("Your balance is: " + str(balance))


@firestore.transactional
def deposit(transaction, doc_ref, deposit_amount):      # function to deposit money to the account
    try:
        snapshot = doc_ref.get(transaction = transaction)
        transaction.update(doc_ref, {"balance": snapshot.get("balance") + deposit_amount})
        return 0
    except:
        print("There was an error while depositing the money")
        return 1


@firestore.transactional
def withdraw(transaction, doc_ref, withdrawal_amount):  # function to withdraw money from the account
    snapshot = doc_ref.get(transaction = transaction)
    balance = snapshot.get("balance")
    if balance < withdrawal_amount:
        print("You do not have enough balance")
        return 1
    else:
        try:                                            # try-except block to handle the error while withdrawing the money
            transaction.update(doc_ref, {"balance": balance - withdrawal_amount})
            return 0
        except:
            print("There was an error while withdrawing the money")
            return 1


def sign_out():                         # function to sign out from the account
    print("You are successfully signed out!")


def logged_in_menu(login, doc_ref, name, last_name):
    while True:                         # loop to show the menu of the services
        print('\nWelcome to the bank, ' + name + ' ' + last_name + '!')
        print('Please type the number of the required service:')
        print('1 - Check balance')
        print('2 - Deposit')
        print('3 - Withdraw')
        print('4 - Transfer')
        print('5 - Sign out')
        service_num = input().strip()
        try:
            service_num = int(service_num)
        except ValueError:
            print("Please type a valid number")
        if service_num == 1:
            check_balance(doc_ref)
        elif service_num == 2:
            deposit_amount = number_request("Please type the amount you want to deposit:")
            transaction = db.transaction()
            deposit(transaction, doc_ref, deposit_amount)
            check_balance(doc_ref)
        elif service_num == 3:
            transaction = db.transaction()
            withdrawal_amount = number_request("Please type the amount you want to withdraw:")
            res = withdraw(transaction, doc_ref, withdrawal_amount)
            check_balance(doc_ref)
        elif service_num == 4:
            recipient_login = name_request("Please type the login name of the account you want to transfer money to:")
            if not if_exists(recipient_login):            # check if the recipient exists
                print("This user does not exist")
                continue
            if recipient_login == login:                    # check if the user wants to transfer money to himself
                print("You cannot transfer money to yourself")
                continue
            sending_amount = number_request("Please type the amount you want to transfer:")
            transaction = db.transaction()
            res = withdraw(transaction, doc_ref, sending_amount)
            if res == 1:                    # check if the withdrawal was successful
                continue
            recipient_ref = db.collection("users").document(recipient_login)
            res = deposit(transaction, recipient_ref, sending_amount)
            if res == 1:                    # check if deposit was successfuk
                continue
            print("The transfer is successfully completed!")
        elif service_num == 5:
            sign_out()
            break
        else:  
            print("Please choose a valid service number")


def start():        # function to start the program
    print("\nWelcome to the bank!")
    while True:
        print("\nPlease type the number of the required service:")
        print("1 - Open an account")
        print("2 - Sign in to account")
        print("9 - Exit")

        service_num = input().strip()
        try:
            service_num = int(service_num)
        except ValueError:
            print("Please type a number")
            return start()
        if service_num == 1:
            open_account()
        elif service_num == 2:
            sign_in()
        elif service_num == 9:
            print("Thank you for choosing our bank. Have a nice day!")
            break
        else:
            print("Please choose a valid service number")
start()