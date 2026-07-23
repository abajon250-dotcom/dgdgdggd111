import re

def validate_russian_phone(phone: str) -> bool:
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and digits.startswith('79'):
        return True
    if len(digits) == 11 and digits.startswith('89'):
        return True
    if len(digits) == 10 and digits.startswith('9'):
        return True
    return False

def normalize_phone(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and digits.startswith('89'):
        return '7' + digits[1:]
    if len(digits) == 10 and digits.startswith('9'):
        return '7' + digits
    return digits