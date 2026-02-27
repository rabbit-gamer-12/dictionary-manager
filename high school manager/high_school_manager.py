from operator import truediv
from cryptography.fernet import Fernet
from email.message import EmailMessage
from datetime import datetime
import difflib, os, json, time, smtplib, random, string, socket


empty_dict = {
}

protected_keys = ["password_main", "email_program", "password_program", "locked", "failed_attempts", "unlock_code", "send_email"]



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# load key
with open("secret.key", "rb") as f:
    key = f.read()



fernet = Fernet(key)

# load encrypted data
with open("codes_passwords.enc", "rb") as f:
    encrypted_data = f.read()

decrypted_data = fernet.decrypt(encrypted_data).decode()
codes_passwords = json.loads(decrypted_data)
password = codes_passwords["password_main"]
email = codes_passwords["email_main"]
progpas = codes_passwords["password_program"]

progeml = codes_passwords["email_program"]
unlock_code = codes_passwords["unlock_code"]
send_alert = codes_passwords["send_email"]
locked = codes_passwords["locked"]
attempts = codes_passwords["failed_attempts"]





with open("windows_shortcuts.json", "r") as w:
    windows_shortcuts = json.load(w)

with open("book_pages.json", "r") as b:
    book_pages = json.load(b)

with open("book_links.json", "r") as l:
    book_links = json.load(l)

with open("dictionary.json", "r") as d:
    dictionary_2 = json.load(d)

with open("available_books.json", "r") as a:
    available_books = json.load(a)

def has_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def alert():
    if has_internet():
        msg = EmailMessage()
        msg["Subject"] = "Securety alert"
        msg["From"] = progeml
        msg["To"] = email
        the_time = datetime.now().strftime("%I:%M %p %d %m %y")
        msg.set_content(f"someone has gaind accses to your passwords at {the_time}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(progeml, progpas)
            smtp.send_message(msg)

        

def alert_email():
    if has_internet():
        codes_passwords["locked"] = True
        length = 16
        nosense = ''.join(random.choice(string.ascii_letters) for _ in range(length))
        codes_passwords["unlock_code"] = nosense
        update()

        msg = EmailMessage()
        msg["Subject"] = "Securety alert"
        msg["From"] = progeml
        msg["To"] = email
        the_time = datetime.now().strftime("%I:%M %p %d %m %y")
        msg.set_content(
    f"Someone tried to access your information and failed at {the_time}.\n\n"
    f"Your unlock code is:\n\n{nosense}"
    "\n\nPlease delete this email!"
)

        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(progeml, progpas)
            smtp.send_message(msg)
        print("allert email sent!")
        codes_passwords["send_email"] = False
        update()
        exit()
        
    else:
        codes_passwords["send_email"] = True
        update()
        exit()

if send_alert:
    alert_email()

def update(name="data"):
    os.system("cls" if os.name == "nt" else "clear")
    print(name, "updated\n")

    # encrypt codes_passwords
    data = json.dumps(codes_passwords, indent=4)
    encrypted = fernet.encrypt(data.encode())

    with open("codes_passwords.enc", "wb") as f:
        f.write(encrypted)

    # normal (non-encrypted) files
    with open("windows_shortcuts.json", "w") as f:
        json.dump(windows_shortcuts, f, indent=4)

    with open("book_pages.json", "w") as f:
        json.dump(book_pages, f, indent=4)

    with open("book_links.json", "w") as f:
        json.dump(book_links, f ,indent=4)

    with open("dictionary.json", "w") as f:
        json.dump(dictionary_2, f, indent=4)

    with open("available_books.json", "w") as f:
        json.dump(available_books, f, indent=4)
    
   

def find_dictionary(dictionary):
    while True:
        key_word = input("enter key word: ").strip().lower()

        if key_word in dictionary:
            if isinstance(dictionary[key_word], list):
                print(key_word, "can mean")
                for i in dictionary[key_word]:
                    print("-", i)
                print()
            else:
                print(key_word, "means.", dictionary[key_word], "\n")
            break
        else:
            matches = difflib.get_close_matches(key_word, dictionary.keys(), n=3)

            if matches:
                print("Did you mean:")
                for word in matches:
                    print("-", word)
            else:
                print("word not found")
                break
  

def find_dict(dictionary):
    global attempts
    attempts = codes_passwords["failed_attempts"]
    logged_in = False

    while True:
        if dictionary == codes_passwords and attempts < 4:
            if not logged_in:
                pin = input("enter password: ")
                if pin == password:
                    logged_in = True
                else:
                    print("access denied")
                    attempts += 1
                    codes_passwords["failed_attempts"] += 1
                    update()
            else:
                os.system("cls" if os.name == "nt" else "clear")

                key_word = input("enter key word: ").strip().lower()
                if key_word in dictionary:
                    if isinstance(dictionary[key_word], list):
                        print("username: ", dictionary[key_word][0])
                        print("password: ", dictionary[key_word][1], "\n")
                        input("press enter to continue")
                        os.system("cls" if os.name == "nt" else "clear")
                        break
                    else:
                        print(dictionary[key_word], "\n")
                        input("press enter to continue")
                        os.system("cls" if os.name == "nt" else "clear")
                        break
                else:
                    matches = difflib.get_close_matches(key_word, dictionary.keys(), n=3)
                    if matches:
                        print("Did you mean:")
                        for word in matches:
                            print("-", word)
                        input("press enter to continue")
                    else:
                        print("word not found")
                        input("press enter to continue")

        elif attempts == 4:
            print("password entered too many times incorrectly")
            alert_email()
            break

        else:
            key_word = input("enter key word: ").strip().lower()
            if key_word in dictionary:
                print(dictionary[key_word], "\n")
                break
            else:
                matches = difflib.get_close_matches(key_word, dictionary.keys(), n=3)
                if matches:
                    print("Did you mean:")
                    for word in matches:
                        print("-", word)
                else:
                    print("word not found")
                    break
        
   
def find_book_pages():
    in_book = False

    while True:
        if not in_book:
            print("available books")
            for i in available_books:
                print("-", i)
            book = input("what book do you want? ").lower()

        if book in available_books:
            topic = input("enter key word: ").strip().lower()
            in_book = True
            if isinstance(book_pages[book][topic], list):
                print(topic, "is on pages")
                for I in book_pages[book][topic]:
                    print(I)
                break
            elif book in book_pages and topic in book_pages[book]:
                print(book_pages[book][topic], "\n")
                break
            else:
                matches = difflib.get_close_matches(topic, book_pages[book].keys(), n=3)
                if matches:
                    print("Did you mean:")
                    for word in matches:
                        print("-", word)
                else:
                    print("word not found")
                    break
        else:
            print("book not found, available book's")
            for i in available_books:
                print("-", i)
            print()

def add(dictionary, name):
    while True:
        print("you can stop at any time by typing qqwertyuiop")

        if name == "book pages":
            b1 = input("new book (1) or edit book (2)? ").strip()
            if b1 == "qqwertyuiop":
                break

            if b1 == "1":
                new_book = input("name your book: ").strip()
                if new_book == "qqwertyuiop":
                    break
                book_pages[new_book] = {}
                available_books.append(new_book)

            elif b1 == "2":
                book_n = input("book name: ").strip()
                if book_n == "qqwertyuiop":
                    break

                l1 = input("make a list? (yes/no): ").strip()
                if l1 == "qqwertyuiop":
                    break

                key_input = input("key word: ").strip()
                if key_input == "qqwertyuiop":
                    break

                if l1 == "yes":
                    values = []
                    while True:
                        value_input = input("value: ").strip()
                        if value_input == "qqwertyuiop":
                            break
                        values.append(value_input)
                    book_pages[book_n][key_input] = values
                else:
                    value_input = input("value: ").strip()
                    if value_input == "qqwertyuiop":
                        break
                    book_pages[book_n][key_input] = value_input
        else:
            l1 = input("make a list? (yes/no): ").strip()
            if l1 == "qqwertyuiop":
                break

            key_input = input("key word: ").strip()
            if key_input in protected_keys and dictionary == codes_passwords:
                print("sorry butt this key is protected")
                return
            if key_input == "qqwertyuiop":
                break

            if l1 == "yes":
                values = []
                while True:
                    value_input = input("value: ").strip()
                    if value_input == "qqwertyuiop":
                        break
                    values.append(value_input)
                dictionary[key_input] = values
            else:
                value_input = input("value: ").strip()
                if value_input == "qqwertyuiop":
                    break
                dictionary[key_input] = value_input

        update(name)


def eddit(dictionary, name):
    print("You can stop at any time by typing 'qqwertyuiop'")

    delete = input("Do you want to delete something? (Y/N): ").strip().upper()
    if delete == "QQWERTYUIOP":
        return

    # ---------- BOOK PAGES ----------
    if name == "book pages":
        print("available books")
        for b in available_books:
            print("-", b)

        if delete == "Y":
            book_del = input("what book do you want to delete? ").strip()
            if book_del == "qqwertyuiop":
                return
            if book_del not in dictionary:
                print("book not found")
                return
            dictionary.pop(book_del)
            available_books.remove(book_del)
            update(name)
            print("Book deleted successfully!")
            return
        else:
            book = input("what book do you want to edit? ").strip().lower()
            if book == "qqwertyuiop":
                return
            if book not in dictionary:
                print("book not found")
                return
            dictionary = dictionary[book]  # go one level deeper

    # ---------- DELETE MODE ----------
    if delete == "Y":
        key_d = input("enter the key you want to delete: ").strip()
        if key_d == "qqwertyuiop":
            return
        if key_d in protected_keys and dictionary == codes_passwords:
            print("sorry, this key is protected")
            return
        if key_d not in dictionary:
            print("key not found")
            return
        dictionary.pop(key_d)
        update(name)
        print("Key deleted successfully!")
        return

    # ---------- EDIT MODE ----------
    key_n = input("enter the key you want to edit: ").strip()
    if key_n == "qqwertyuiop":
        return
    if key_n in protected_keys and dictionary == codes_passwords:
        print("sorry, this key is protected")
        return
    if key_n not in dictionary:
        print("key not found")
        return

    value = dictionary[key_n]

    # ---------- LIST VALUE ----------
    if isinstance(value, list):
        print("this key stores a list:")
        for i, v in enumerate(value):
            print(i, "-", v)

        choice = input("replace whole list (1) or edit one item (2): ").strip()
        if choice == "qqwertyuiop":
            return

        if choice == "1":
            new_list = []
            print("enter new list values (qqwertyuiop to stop)")
            while True:
                v = input("value: ").strip()
                if v == "qqwertyuiop":
                    break
                new_list.append(v)
            dictionary[key_n] = new_list

        elif choice == "2":
            idx = input("which index do you want to edit? ").strip()
            if idx == "qqwertyuiop":
                return
            idx = int(idx)
            if 0 <= idx < len(value):
                new_v = input("new value: ").strip()
                if new_v == "qqwertyuiop":
                    return
                value[idx] = new_v
            else:
                print("invalid index")
                return

    # ---------- NON-LIST VALUE ----------
    else:
        new_v = input(f"what do you want '{key_n}' to store? ").strip()
        if new_v == "qqwertyuiop":
            return
        dictionary[key_n] = new_v

    update(name)
    print("Updated successfully!\n")



  
available_dicts_and_actions  = ["dictionary", "book links", "codes/passwords(password protected)", "book pages", "windows shortcuts", "add to", "eddit", "change password", "stop"]
available_dicts = [ "dictionary", "book links", "codes/passwords(password protected)", "book pages", "windows shortcuts"]
available_numbers = ["1", "2", "3", "4", "5"]

if locked:
    unlock_123 = input("to unlock accses to your password please enter the unlock code that we sent to your email ")
    if unlock_123 == unlock_code:
        print("yay!")
        codes_passwords["locked"] = False
        codes_passwords["unlock_code"] = None
        codes_passwords["failed_attempts"] = 0
        update()
        locked = codes_passwords["locked"]
        attempts = codes_passwords["failed_attempts"]
        unlock_code = codes_passwords["unlock_code"]
    else:
        print("wrong code")

while True:
    


    if email == "":
        em1 = input("pleases enter your email ")
        em2 = input("please confirm your email ")
        codes_passwords["email_main"] = em2
        update("email")

    if password == "":
        pe1 = input("please enter a password ")
        pe2 = input("please conferm password ")
        if pe1 == pe2:
            codes_passwords["password_main"] = pe1
            password = pe1
            update("password")
    numb = 1
    for num in available_dicts_and_actions:
        print("-", numb, num)
        numb += 1
    input_dict = input("what dictionary or action do you want? ").strip().lower()
    numb = 0

    if input_dict in ["stop", "9"]:
        update("all dictionaries")
        print("Goodbye!")
        time.sleep(0.5)
        os.system("cls" if os.name == "nt" else "clear")
        break
    elif attempts == 4:
            print("password entered too many times incorrectly")
            alert_email()
            exit()
    
    elif input_dict in ("dictionary", "1"):
        find_dictionary(dictionary_2)
    elif input_dict in ("book links", "2"):
        find_dict(book_links)
    elif input_dict in ("codes", "passwords", "3"):
        alert()
        find_dict(codes_passwords)
    elif input_dict in ("book pages", "4"):
        find_book_pages()
    elif input_dict in ("windows shortcuts", "5"):
        find_dict(windows_shortcuts)
    elif input_dict in ["add to", "6"]:
        dictionary_add = input("what dictionary do you want to add to? ")
        if dictionary_add in available_dicts or dictionary_add in available_numbers:
            
            if dictionary_add in ["dictionary", "1"]:
                add(dictionary_2, "dictionary")
            elif dictionary_add in ["book links", "2"]:
                add(book_links, "book links")
            elif dictionary_add in ["book pages", "4"]:
                add(book_pages, "book pages")
            elif dictionary_add in ["windows shortcuts", "5"]:
                add(windows_shortcuts, "windows shortcuts")
            

            elif dictionary_add in ["codes", "passwords", "3"]:
                pin = input("pleass enter password: ")
                os.system("cls" if os.name == "nt" else "clear")
                if attempts >= 4:
                    alert_email()
                if pin == password:
                    alert()
                    add(codes_passwords, "codes_passwords")
                    
                else:
                    print("accses denied")
                    attempts += 1
                    codes_passwords["failed_attempts"] += 1
                    update()
        else:
            print("dictionary not found")
            print("available dictionaries")
            for i in available_dicts:
                print("-", i)
    
    elif input_dict in ["eddit", "7"]:
        dictionary_eddit = input("what dictionary do you want to eddit ")
        if dictionary_eddit in available_dicts or dictionary_eddit in available_numbers:
            
            if dictionary_eddit in ["dictionary", "1"]:
                eddit(dictionary_2, "dictionary")
            elif dictionary_eddit in ["book links", "2"]:
                eddit(book_links, "book links")
            elif dictionary_eddit in ["book pages", "4"]:
                eddit(book_pages, "book pages")
            elif dictionary_eddit in ["windows shortcuts", "5"]:
                eddit(windows_shortcuts, "windows shortcuts")
            

            elif dictionary_eddit in ["codes", "passwords", "3"]:
                pin = input("pleass enter password: ")
                os.system("cls" if os.name == "nt" else "clear")
                if attempts >= 4:
                    alert_email()
                if pin == password:
                    alert()
                    eddit(codes_passwords, "codes_passwords")
                    
                else:
                    print("accses denied")
                    attempts += 1
                    codes_passwords["failed_attempts"] += 1
                    update()
        else:
            print("dictionary not found")
            print("available dictionaries")
            for i in available_dicts:
                print("-", i)

    elif input_dict in ["change password", "8"]:
        cp = input("please enter current password: ")
        os.system("cls" if os.name == "nt" else "clear")
        if attempts >= 4:
            alert_email()
        if cp == password:
            pe1 = input("please enter new pasword: ")
            pe2 = input("please confurme new pasword: ")
            os.system("cls" if os.name == "nt" else "clear")
            if pe1 == pe2:
                password = pe1
                codes_passwords["password_main"] = pe1
                update("password")  
        else:
            print("accses denied")
            attempts += 1
            codes_passwords["failed_attempts"] += 1
            update()
    else:
        print("dictionary not found")
        print("here are the available dictionaries and actions")
        for i in available_dicts_and_actions:
            print("-", i)

