
import plivo
import re
import random

def send_sms(dst, text, src="16502647255"):
    rest_api = plivo.RestAPI(app.config['PLIVO_AUTH_ID'], app.config['PLIVO_AUTH_TOKEN'])
    # strip other chars (space + - etc)
    dst_cleaned = re.sub('[^0-9]*', '', dst)
    #TODO: check HTTP status code and handle case where this fails
    return rest_api.send_message({'src': src, 'dst': dst_cleaned, 'text': text})


def send_sms_message(number, message):
    ''' generic function to send sms message to number '''
    api = RestAPI(settings.PLIVO['id'], settings.PLIVO['token'])
    return api.send_message({
            'text': message,
            'src':  settings.PLIVO['src'],
            'dst':  '1' + number,
        })

def get_random_number():
	characters2='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	otp=''
 	n2=5
	for i in range(0,n2):
		num2=random.randint(0,len(characters2)-1)
		otp=otp+characters2[num2]
	#otp_first=hashlib.sha1(otp).hexdigest()
	#random_number=hashlib.md5(otp_first).hexdigest()
	return otp

def send_sms(text, phone_number):
	#print(Constant.plivo_auth_id)
	#return Constant.plivo_auth_id
	p = plivo.RestAPI('MAMZRJZMMWM2RLNTG2MD','ZWZlZTA2YTZkZjEzNmJjZmFmYjQyYTc3NGY0NDU4')
	params = {
		'src': 'KIET-ERP',
		'dst': '+91' + str(phone_number),
		'text': text
	}
	p.send_message(params)