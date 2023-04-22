# SecurityManager.py

import sqlite3
import logging
import os
import smtplib
import email.message
from cryptography.fernet import Fernet
from hashlib import pbkdf2_hmac
from base64 import b64encode, b64decode
import secrets

DB_NAME = "security_manager.db"
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

# Configure logging
logging.basicConfig(filename="security_manager.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def generate_salt():
    return secrets.token_bytes(16)

def hash_password(password, salt):
    password_hash = pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt, b64encode(password_hash)

def verify_password(password, salt, password_hash):
    salt = b64decode(salt)
    stored_hash = b64decode(password_hash)
    password_hash = pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return password_hash == stored_hash

def generate_token():
    return secrets.randbelow(1000000)

def register_user(username, password, email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            raise Exception("User already exists")
        else:
            salt, password_hash = hash_password(password, generate_salt())
            token = generate_token()
            cursor.execute("INSERT INTO users (username, salt, password, token, email, timestamp, role) VALUES (?, ?, ?, ?, ?, datetime('now'), 'user')", (username, salt, password_hash, token, email))
            conn.commit()
            return token

def authenticate_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            salt = user[1]
            password_hash = user[2]
            if verify_password(password, salt, password_hash):
                return user[4], user[6]  # Return email and role
            else:
                raise Exception("Wrong password")
        else:
            raise Exception("User not found")

def revoke_or_renew_token(username, password, action):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            salt = user[1]
            password_hash = user[2]
            if verify_password(password, salt, password_hash):
                if action == "revoke":
                    cursor.execute("UPDATE users SET token = 0 WHERE username = ?", (username,))
                    conn.commit()
                    return "Token revoked successfully"
                elif action == "renew":
                    new_token = generate_token()
                    cursor.execute("UPDATE users SET token = ?, timestamp = datetime('now') WHERE username = ?", (new_token, username))
                    conn.commit()
                    return new_token
                else:
                    raise Exception("Invalid action")
            else:
                raise Exception("Wrong password")
        else:
            raise Exception("User not found")

def change_password(username, old_password, new_password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            old_salt = user[1]
            old_password_hash = user[2]
            if verify_password(old_password, old_salt, old_password_hash):
                new_salt, new_password_hash = hash_password(new_password)
                cursor.execute("UPDATE users SET salt = ?, password = ?, timestamp = datetime('now') WHERE username = ?", (new_salt, new_password_hash, username))
                conn.commit()
                return "Password changed successfully"
            else:
                raise Exception("Wrong old password")
        else:
            raise Exception("User not found")

def reset_password(username, reset_code, new_password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            with open("reset_codes.txt", "r") as f:
                for line in f:
                    user_code, stored_reset_code = line.split()
                    if user_code == username and reset_code == stored_reset_code:
                        salt, password_hash = hash_password(new_password)
                        cursor.execute("UPDATE users SET salt = ?, password = ?, timestamp = datetime('now') WHERE username = ?", (salt, password_hash, username))
                        conn.commit()
                        return "Password reset successfully"
                else:
                    raise Exception("Invalid reset code")
        else:
            raise Exception("User not found")

def delete_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            salt = user[1]
            password_hash = user[2]
            if verify_password(password, salt, password_hash):
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                return "User deleted successfully"
            else:
                raise Exception("Wrong password")
        else:
            raise Exception("User not found")

def assign_role(username, role):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
            conn.commit()
            return "Role assigned successfully"
        else:
            raise Exception("User not found")

def encrypt_data(data, key):
    fernet = Fernet(key)
    data_bytes = data.encode()
    encrypted_data = fernet.encrypt(data_bytes)
    return encrypted_data

def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    data_bytes = fernet.decrypt(encrypted_data)
    data = data_bytes.decode()
    return data

def audit_action(username, action, status):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit (username, action, status, timestamp) VALUES (?, ?, ?, datetime('now'))", (username, action, status))
        conn.commit()
        logging.info(f"{username} {action} {status}")

def notify_event(username, event, email):
    message = email.message.EmailMessage()
    message["Subject"] = "Security Event Notification"
    message["From"] = EMAIL_USER
    message["To"] = email
    message.set_content(f"Hello {username},\n\nWe detected a security event on your account. The event details are as follows:\n\n{event}\n\nIf you recognize this event, please ignore this email. Otherwise, please take the following actions to secure your account:\n\n- Change your password immediately.\n- Revoke or renew your token.\n- Contact the administrator for further assistance.\n\nThank you,\nSecurityManager.py Team")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(message)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt BLOB NOT NULL, password BLOB NOT NULL, token INTEGER NOT NULL, email TEXT NOT NULL, timestamp INTEGER NOT NULL, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, username TEXT NOT NULL, action TEXT NOT NULL, status TEXT NOT NULL, timestamp INTEGER NOT NULL)")

    conn.close()
    