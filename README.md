Secure Dictionary Program
=========================

This is a Python-based secure dictionary and password manager program.
It allows you to store, search, add, edit, and protect information using
encryption and password-based access control.

Sensitive data is encrypted using the cryptography library (Fernet).


Requirements
------------
- Python 3.10 or newer
- Internet connection (only required for email alerts)
- The cryptography Python package


Installation (Windows)
----------------------

1. Install Python
   - Go to https://www.python.org/downloads/
   - Download Python for Windows
   - IMPORTANT: Check "Add Python to PATH" during installation

2. Download the Program
   - Click the green "Code" button on GitHub
   - Choose "Download ZIP"
   - Extract the folder to your computer (Desktop is fine)

3. Open Windows PowerShell
   - Press Win + R
   - Type: powershell
   - Press Enter

4. Navigate to the Project Folder
   Example:
   cd Desktop\your-project-folder-name

5. Install Required Packages
   Run:
   python -m pip install -r requirements.txt


Running the Program
-------------------

Run the program using:
python main.py

(Replace main.py with the actual filename if different)


Security Notes
--------------
- DO NOT upload or share the following files:
  - secret.key
  - codes_passwords.enc

These files contain encrypted or sensitive information.

If you upload this project to GitHub:
- Add secret.key and *.enc to .gitignore
- Use example or empty data files only


Features
--------
- Encrypted password storage
- Password-protected access
- Failed login detection
- Email alerts for suspicious activity
- Editable dictionaries and book pages
- Secure lock and unlock system
- Language management system

Author
------
Created by Reilly Martin
