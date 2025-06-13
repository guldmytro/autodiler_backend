import base64
import hashlib
import ecdsa
import requests
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

PUBKEY_PATH = os.path.join(settings.BASE_DIR, "monobank_pubkey.pem")

def fix_base64_padding(b64_str: str) -> str:
    return b64_str + "=" * (-len(b64_str) % 4)


def fetch_monobank_pubkey() -> str:
    """
    Завантажує новий відкритий ключ з Monobank API.
    """
    logger.info("🔄 Завантаження нового публічного ключа з Monobank API...")
    headers = {'X-Token': settings.MONOBANK_TOKEN}
    response = requests.get("https://api.monobank.ua/api/merchant/pubkey", headers=headers, timeout=10)
    response.raise_for_status()
    logger.info("✅ Новий публічний ключ отримано")
    return response.text  # PEM-формат


def load_cached_pubkey() -> str:
    """
    Читає кешований публічний ключ з файлу.
    """
    logger.info(f"📂 Завантаження кешованого ключа з файлу: {PUBKEY_PATH}")
    with open(PUBKEY_PATH, "r") as f:
        pem = f.read()
    logger.info("✅ Кешований ключ завантажено")
    return pem


def save_pubkey(pubkey_pem: str):
    """
    Зберігає публічний ключ у файл.
    """
    logger.info(f"💾 Збереження публічного ключа у файл: {PUBKEY_PATH}")
    with open(PUBKEY_PATH, "w") as f:
        f.write(pubkey_pem)
    logger.info("✅ Ключ збережено")


def verify_signature(signature_base64: str, body_bytes: bytes, pubkey_pem: str) -> bool:
    """
    Перевіряє підпис webhook від Monobank.
    """
    logger.info("🔐 Перевірка підпису...")
    try:
        signature_bytes = base64.b64decode(fix_base64_padding(signature_base64))
        pub_key = ecdsa.VerifyingKey.from_pem(pubkey_pem)
        ok = pub_key.verify(signature_bytes, body_bytes, sigdecode=ecdsa.util.sigdecode_der, hashfunc=hashlib.sha256)
        logger.info("✅ Підпис валідний")
        return ok
    except Exception as e:
        logger.warning(f"❌ Помилка валідації підпису: {e}")
        return False


def verify_with_fallback(signature_base64: str, body_bytes: bytes) -> bool:
    """
    Перевіряє підпис, а при помилці — оновлює ключ і пробує знову.
    """
    logger.info("🚦 Початок перевірки підпису з кешованим ключем...")
    try:
        pubkey_pem = load_cached_pubkey()
        if verify_signature(signature_base64, body_bytes, pubkey_pem):
            logger.info("✅ Підпис пройшов перевірку з кешованим ключем")
            return True
        else:
            logger.warning("⚠️ Підпис НЕ пройшов перевірку з кешованим ключем")
    except Exception as e:
        logger.warning(f"⚠️ Помилка при роботі з кешованим ключем: {e}")

    logger.info("🔁 Спроба оновити публічний ключ і повторити перевірку...")
    try:
        pubkey_pem = fetch_monobank_pubkey()
        save_pubkey(pubkey_pem)
        if verify_signature(signature_base64, body_bytes, pubkey_pem):
            logger.info("✅ Підпис пройшов перевірку з оновленим ключем")
            return True
        else:
            logger.error("❌ Підпис НЕ пройшов перевірку навіть з оновленим ключем")
    except Exception as e:
        logger.error(f"❌ Не вдалося оновити публічний ключ або верифікувати підпис: {e}")

    return False
