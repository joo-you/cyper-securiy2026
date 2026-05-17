from cryptography.fernet import Fernet

from django.conf import settings

cipher = Fernet(
    settings.CHAT_SECRET_KEY
)

def encrypt_message(message):

    encrypted =
    cipher.encrypt(
        message.encode()
    )

    return encrypted.decode()


def decrypt_message(message):

    decrypted =
    cipher.decrypt(
        message.encode()
    )

    return decrypted.decode()