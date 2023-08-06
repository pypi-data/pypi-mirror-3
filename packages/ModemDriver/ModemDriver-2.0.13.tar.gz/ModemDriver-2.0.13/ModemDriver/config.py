# AT command timeout in second
timeout = 30

# AT+CNMI=<init>
init_sms = {
    'MC388': '1,1',
    'MC389': '1,1',
    'C55': '0,0,0,0,1',
    'M55': '0,0,0,0,1',
    'MC60': '0,0,0,0,1',
    'A60': '0,0,0,0,1',
    'Nokia 9300i': '1,1,0,0,0',
    'Nokia 6080': '1,1,0,0,0',
    'Motorola': '3,1',
    'C380': '3,1',
    'TR-800': '2,1,0,0,0',
    'Billionton': '2,1,0,0,1',
    'MF110': '2,1,0,0,0',
    }

# AT+CSCA=<smsc>
# Dictionary diisi key = imei chip, value = SMS center
smsc = {'510011130802951': '+62816124'}

memory_sms = {
    'Billionton': ['MT', 'SM'], # machine and sim memory
    }

# GSM biasanya bisa PDU mode (SMS lebih dari 160 karakter)
pdu_mode = ['C55', 'M55', 'MC60', 'A60', 'MULTIBAND  900E  1800']

# Beberapa modem tidak bisa kirim SMS ke nomor dengan awalan + (international
# format), cukup hilangkan awalan itu. Contohnya terjadi pada Wavecom CDMA.
sms_dest_without_sign = ['WAVECOM MODEM 800 1900']


# ATD<ussd>;
ussd_use_atd = ['C55', 'M55', 'MC60', 'A60', 'TR-800',
    'WAVECOM MODEM 800 1900']

# Modem seperti iTegno W3800 (TR-800) tidak mengenal karakter ENTER "\n"
# sehingga perlu diganti SPACE " " agar tidak merapat.
unrecognize_character = { 
    'TR-800': ['\n'],
    }

# External script. Isi dengan command line
event = {
    'call': '',
    'sms': '',
    }
