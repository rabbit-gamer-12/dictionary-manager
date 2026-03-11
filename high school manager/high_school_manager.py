from __future__ import annotations

import difflib
import getpass
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


STOP_WORD = "qqwertyuiop"
MAX_FAILED_ATTEMPTS = 4


@dataclass
class SecureVault:
    """Encrypted storage for private credentials and app security state."""

    directory: Path

    def __post_init__(self) -> None:
        self.key_file = self.directory / "secret.key"
        self.encrypted_file = self.directory / "codes_passwords.enc"
        self.data: dict[str, Any] = {}
        self._fernet = Fernet(self._load_or_create_key())
        self._load_or_create_encrypted_data()

    def _load_or_create_key(self) -> bytes:
        if self.key_file.exists():
            return self.key_file.read_bytes()

        key = Fernet.generate_key()
        self.key_file.write_bytes(key)
        return key

    def _default_data(self) -> dict[str, Any]:
        return {
            "password_main": "",
            "email_main": "",
            "failed_attempts": 0,
            "locked": False,
            "unlock_code": None,
            "notes": {},
        }

    def _load_or_create_encrypted_data(self) -> None:
        if not self.encrypted_file.exists():
            self.data = self._default_data()
            self.save()
            return

        try:
            encrypted = self.encrypted_file.read_bytes()
            decrypted = self._fernet.decrypt(encrypted).decode("utf-8")
            self.data = json.loads(decrypted)
        except (InvalidToken, json.JSONDecodeError):
            print("⚠️ Vault data was unreadable. Creating a fresh vault file.")
            self.data = self._default_data()
            self.save()

        # Add missing keys in older versions.
        defaults = self._default_data()
        for key, value in defaults.items():
            self.data.setdefault(key, value)

    def save(self) -> None:
        payload = json.dumps(self.data, indent=2).encode("utf-8")
        encrypted = self._fernet.encrypt(payload)
        self.encrypted_file.write_bytes(encrypted)

    @property
    def is_locked(self) -> bool:
        return bool(self.data.get("locked", False))

    @property
    def failed_attempts(self) -> int:
        return int(self.data.get("failed_attempts", 0))

    def ensure_master_password(self) -> None:
        if self.data["password_main"]:
            return

        print("\nLet's set up your master password.")
        while True:
            first = getpass.getpass("Create master password: ")
            second = getpass.getpass("Confirm master password: ")
            if not first:
                print("Password cannot be empty.")
                continue
            if first != second:
                print("Passwords do not match. Try again.")
                continue
            self.data["password_main"] = first
            self.data["failed_attempts"] = 0
            self.save()
            print("Master password saved.\n")
            return

    def authenticate(self) -> bool:
        if self.is_locked:
            print("This vault is locked due to too many failed attempts.")
            return False

        entered = getpass.getpass("Master password: ")
        if entered == self.data["password_main"]:
            self.data["failed_attempts"] = 0
            self.save()
            return True

        self.data["failed_attempts"] = self.failed_attempts + 1
        if self.failed_attempts >= MAX_FAILED_ATTEMPTS:
            self.data["locked"] = True
            print("Vault has been locked after too many failed attempts.")
        else:
            remaining = MAX_FAILED_ATTEMPTS - self.failed_attempts
            print(f"Incorrect password. Attempts remaining: {remaining}")
        self.save()
        return False

    def reset_lock(self) -> None:
        self.data["locked"] = False
        self.data["failed_attempts"] = 0
        self.save()


class JSONStore:
    """Persistent JSON files for dictionary-style content."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.files: dict[str, str] = {
            "dictionary": "dictionary.json",
            "book_links": "book_links.json",
            "book_pages": "book_pages.json",
            "windows_shortcuts": "windows_shortcuts.json",
            "languages": "languages.json",
            "available_books": "available_books.json",
        }
        self.data: dict[str, Any] = {}
        self._load_or_create_all()

    def _load_or_create_all(self) -> None:
        defaults: dict[str, Any] = {
            "dictionary": {},
            "book_links": {},
            "book_pages": {},
            "windows_shortcuts": {},
            "languages": {},
            "available_books": [],
        }

        for key, filename in self.files.items():
            path = self.directory / filename
            if not path.exists():
                path.write_text(json.dumps(defaults[key], indent=2), encoding="utf-8")
            try:
                self.data[key] = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.data[key] = defaults[key]
                path.write_text(json.dumps(defaults[key], indent=2), encoding="utf-8")

    def save(self, key: str) -> None:
        filename = self.files[key]
        path = self.directory / filename
        path.write_text(json.dumps(self.data[key], indent=2), encoding="utf-8")


class DictionaryManagerApp:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.store = JSONStore(root_dir)
        self.vault = SecureVault(root_dir)

    def run(self) -> None:
        print("=== Dictionary Manager ===")
        self.vault.ensure_master_password()

        while True:
            self._print_main_menu()
            choice = input("Choose an option: ").strip().lower()

            if choice in {"0", "exit", "quit"}:
                print("Goodbye!")
                return
            if choice in {"1", "dictionary"}:
                self._dictionary_menu("dictionary")
            elif choice in {"2", "book links"}:
                self._dictionary_menu("book_links")
            elif choice in {"3", "windows shortcuts"}:
                self._dictionary_menu("windows_shortcuts")
            elif choice in {"4", "languages"}:
                self._languages_menu()
            elif choice in {"5", "book pages"}:
                self._book_pages_menu()
            elif choice in {"6", "vault"}:
                self._vault_menu()
            elif choice in {"7", "unlock vault"}:
                self.vault.reset_lock()
                print("Vault lock has been reset.")
            else:
                print("Invalid choice.")

    def _print_main_menu(self) -> None:
        print(
            "\n1) Dictionary\n"
            "2) Book links\n"
            "3) Windows shortcuts\n"
            "4) Languages\n"
            "5) Book pages\n"
            "6) Vault (password protected notes)\n"
            "7) Unlock vault\n"
            "0) Exit"
        )

    def _dictionary_menu(self, key: str) -> None:
        data: dict[str, Any] = self.store.data[key]
        while True:
            print("\n1) List all\n2) Search\n3) Add\n4) Edit\n5) Delete\n0) Back")
            action = input("Action: ").strip().lower()

            if action in {"0", "back"}:
                return
            if action == "1":
                self._list_all(data)
            elif action == "2":
                term = input("Search key: ").strip().lower()
                if term == STOP_WORD:
                    continue
                self._search_and_print(data, term)
            elif action == "3":
                self._add_entry(data)
                self.store.save(key)
            elif action == "4":
                self._edit_entry(data)
                self.store.save(key)
            elif action == "5":
                self._delete_entry(data)
                self.store.save(key)
            else:
                print("Invalid action.")

    def _languages_menu(self) -> None:
        languages: dict[str, dict[str, str]] = self.store.data["languages"]
        while True:
            print("\n1) Translate\n2) Add translation\n3) Edit translation\n4) Delete translation\n0) Back")
            action = input("Action: ").strip()

            if action == "0":
                return
            if action == "1":
                word = input("Word: ").strip().lower()
                if word in languages:
                    print(json.dumps(languages[word], indent=2, ensure_ascii=False))
                else:
                    print("Word not found.")
            elif action == "2":
                word = input("Word: ").strip().lower()
                lang = input("Language: ").strip().lower()
                value = input("Translation: ").strip()
                languages.setdefault(word, {})[lang] = value
                self.store.save("languages")
                print("Saved.")
            elif action == "3":
                word = input("Word: ").strip().lower()
                lang = input("Language: ").strip().lower()
                if word not in languages or lang not in languages[word]:
                    print("Translation not found.")
                    continue
                languages[word][lang] = input("New translation: ").strip()
                self.store.save("languages")
                print("Updated.")
            elif action == "4":
                word = input("Word: ").strip().lower()
                lang = input("Language: ").strip().lower()
                if word in languages and lang in languages[word]:
                    del languages[word][lang]
                    if not languages[word]:
                        del languages[word]
                    self.store.save("languages")
                    print("Deleted.")
                else:
                    print("Translation not found.")
            else:
                print("Invalid action.")

    def _book_pages_menu(self) -> None:
        pages: dict[str, dict[str, Any]] = self.store.data["book_pages"]
        books: list[str] = self.store.data["available_books"]

        while True:
            print("\n1) List books\n2) Search page topic\n3) Add/Edit topic\n4) Add new book\n5) Delete book\n0) Back")
            action = input("Action: ").strip()

            if action == "0":
                return
            if action == "1":
                print("Books:")
                for book in books:
                    print(f"- {book}")
            elif action == "2":
                book = input("Book name: ").strip().lower()
                if book not in pages:
                    print("Book not found.")
                    continue
                topic = input("Topic: ").strip().lower()
                if topic in pages[book]:
                    print(f"{topic}: {pages[book][topic]}")
                else:
                    print("Topic not found.")
            elif action == "3":
                book = input("Book name: ").strip().lower()
                if book not in pages:
                    print("Book not found.")
                    continue
                topic = input("Topic: ").strip().lower()
                value = input("Page(s): ").strip()
                pages[book][topic] = value
                self.store.save("book_pages")
                print("Saved.")
            elif action == "4":
                book = input("New book name: ").strip().lower()
                if book in pages:
                    print("Book already exists.")
                    continue
                pages[book] = {}
                books.append(book)
                self.store.save("book_pages")
                self.store.save("available_books")
                print("Book created.")
            elif action == "5":
                book = input("Book name to delete: ").strip().lower()
                if book not in pages:
                    print("Book not found.")
                    continue
                del pages[book]
                if book in books:
                    books.remove(book)
                self.store.save("book_pages")
                self.store.save("available_books")
                print("Book deleted.")
            else:
                print("Invalid action.")

    def _vault_menu(self) -> None:
        if not self.vault.authenticate():
            return

        notes: dict[str, str] = self.vault.data.setdefault("notes", {})
        while True:
            print("\n1) List notes\n2) Get note\n3) Add/Edit note\n4) Delete note\n5) Change master password\n0) Back")
            action = input("Action: ").strip()

            if action == "0":
                self.vault.save()
                return
            if action == "1":
                self._list_all(notes)
            elif action == "2":
                self._search_and_print(notes, input("Note key: ").strip().lower())
            elif action == "3":
                key = input("Note key: ").strip().lower()
                notes[key] = input("Note value: ").strip()
                self.vault.save()
                print("Saved.")
            elif action == "4":
                key = input("Note key: ").strip().lower()
                notes.pop(key, None)
                self.vault.save()
                print("Deleted if it existed.")
            elif action == "5":
                self._change_master_password()
            else:
                print("Invalid action.")

    def _change_master_password(self) -> None:
        old = getpass.getpass("Current password: ")
        if old != self.vault.data["password_main"]:
            print("Current password is incorrect.")
            return
        new_one = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")
        if not new_one or new_one != confirm:
            print("Passwords did not match.")
            return
        self.vault.data["password_main"] = new_one
        self.vault.save()
        print("Master password updated.")

    @staticmethod
    def _list_all(data: dict[str, Any]) -> None:
        if not data:
            print("No entries yet.")
            return
        for key, value in data.items():
            print(f"- {key}: {value}")

    @staticmethod
    def _search_and_print(data: dict[str, Any], term: str) -> None:
        if term in data:
            print(f"{term}: {data[term]}")
            return
        matches = difflib.get_close_matches(term, data.keys(), n=3)
        if matches:
            print("Did you mean:")
            for match in matches:
                print(f"- {match}")
        else:
            print("Not found.")

    @staticmethod
    def _add_entry(data: dict[str, Any]) -> None:
        key = input("Key: ").strip().lower()
        if key == STOP_WORD:
            return
        if key in data:
            print("Key already exists.")
            return
        data[key] = input("Value: ").strip()
        print("Added.")

    @staticmethod
    def _edit_entry(data: dict[str, Any]) -> None:
        key = input("Key to edit: ").strip().lower()
        if key not in data:
            print("Key not found.")
            return
        data[key] = input("New value: ").strip()
        print("Updated.")

    @staticmethod
    def _delete_entry(data: dict[str, Any]) -> None:
        key = input("Key to delete: ").strip().lower()
        if key in data:
            del data[key]
            print("Deleted.")
        else:
            print("Key not found.")


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    os.chdir(root_dir)
    app = DictionaryManagerApp(root_dir)
    app.run()


if __name__ == "__main__":
    main()
