import base64
import hashlib
import ecdsa
import requests
import os
from django.conf import settings


PUBKEY_PATH = os.path.join(settings.BASE_DIR, "monobank_pubkey.pem")


def fetch_monobank_pubkey() -> str:
    """
    Завантажує новий відкритий ключ з Monobank API.
    """
    print("🔄 Завантаження нового публічного ключа з Monobank API...")
    headers = {'X-Token': settings.MONOBANK_TOKEN}
    response = requests.get("https://api.monobank.ua/api/merchant/pubkey", headers=headers, timeout=10)
    response.raise_for_status()
    print("✅ Новий публічний ключ отримано")
    return response.text  # PEM-формат


def load_cached_pubkey() -> str:
    """
    Читає кешований публічний ключ з файлу.
    """
    print(f"📂 Завантаження кешованого ключа з файлу: {PUBKEY_PATH}")
    with open(PUBKEY_PATH, "r") as f:
        pem = f.read()
    print("✅ Кешований ключ завантажено")
    return pem


def save_pubkey(pubkey_pem: str):
    """
    Зберігає публічний ключ у файл.
    """
    print(f"💾 Збереження публічного ключа у файл: {PUBKEY_PATH}")
    with open(PUBKEY_PATH, "w") as f:
        f.write(pubkey_pem)
    print("✅ Ключ збережено")


def verify_signature(signature_base64: str, body_bytes: bytes, pubkey_pem: str) -> bool:
    """
    Перевіряє підпис webhook від Monobank.
    """
    print("🔐 Перевірка підпису...")
    try:
        signature_bytes = base64.b64decode(signature_base64)
        pub_key = ecdsa.VerifyingKey.from_pem(pubkey_pem)
        ok = pub_key.verify(signature_bytes, body_bytes, sigdecode=ecdsa.util.sigdecode_der, hashfunc=hashlib.sha256)
        print("✅ Підпис валідний")
        return ok
    except Exception as e:
        print(f"❌ Помилка валідації підпису: {e}")
        return False


def verify_with_fallback(signature_base64: str, body_bytes: bytes) -> bool:
    """
    Перевіряє підпис, а при помилці — оновлює ключ і пробує знову.
    """
    print("🚦 Початок перевірки підпису з кешованим ключем...")
    try:
        pubkey_pem = load_cached_pubkey()
        if verify_signature(signature_base64, body_bytes, pubkey_pem):
            print("✅ Підпис пройшов перевірку з кешованим ключем")
            return True
        else:
            print("⚠️ Підпис НЕ пройшов перевірку з кешованим ключем")
    except Exception as e:
        print(f"⚠️ Помилка при роботі з кешованим ключем: {e}")

    print("🔁 Спроба оновити публічний ключ і повторити перевірку...")
    try:
        pubkey_pem = fetch_monobank_pubkey()
        save_pubkey(pubkey_pem)
        if verify_signature(signature_base64, body_bytes, pubkey_pem):
            print("✅ Підпис пройшов перевірку з оновленим ключем")
            return True
        else:
            print("❌ Підпис НЕ пройшов перевірку навіть з оновленим ключем")
    except Exception as e:
        print(f"❌ Не вдалося оновити публічний ключ або верифікувати підпис: {e}")

    return False
