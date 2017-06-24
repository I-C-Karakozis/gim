from app import app

import re

def meets_password_requirements(password):
    len_req = len(password) >= app.config.get('MIN_PASS_LEN')
    letter_req = re.search('[A-Za-z]', password)
    number_req = re.search('\\d', password)
    punctuation_req = re.search('[^A-Za-z0-9]', password)
    return len_req and letter_req and number_req and punctuation_req