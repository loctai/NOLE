import uuid
import coinaddr
from decimal import Decimal
import requests
from config import Config
def getNextSequence(collection,name):
    if not collection.find_one({'_id': name}) :
        collection.insert_one({ "_id": name, "seq" : 0 })
    return collection.find_and_modify(query= { '_id': name },update= { '$inc': {'seq': 1}}, new=True ).get('seq')

def generate_username(number):
    uid = uuid.uuid4()
    _id = str(uid.fields[-1])[:8]
    new_id = str(number)+str(_id)
    return str(new_id)[0:8]

def generate_transaction_id(number):
    uid = uuid.uuid4()
    _id = str(uid.fields[-1])[:8]
    new_id = str(number)+str(_id)
    return str(new_id)[0:8]

def get_tickers(collection, currency=None):
    dataTicker = collection.find_one({})
    if currency:
        return dataTicker[currency+'_price']
    return dataTicker

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

def format_usd(value):
    amount = round(float(value), 2)
    return "{:,.2f}".format(amount)


def format_btc(btc):
    if btc == 0:
        return '0.00'
    btc = Decimal(btc)
    def remove_exponent(d):
        '''Remove exponent and trailing zeros.
        >>> remove_exponent(Decimal('5E+3'))
        Decimal('5000')
        '''
        return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
    val = str(btc)
    if val.find('.') != -1:
        val = val.rstrip('0')
        if val[-1] == '.':
            val += '0'
    return val
def format_satoshi(satoshi):
    if float(satoshi) < 100:
        return '0.00'
    return format_btc(Decimal(satoshi) / 10**8)

def format_time(t):
    return strftime('%Y-%m-%d %H:%M:%S',gmtime(t))

def verify_address(addr, currency):
    try:
        if currency == 'trx' or currency == 'TRX' or currency == 'qtc' or currency == 'QTC':
            return 1
        result = coinaddr.validate(currency.lower(), addr)
        # print(result)
        if 'valid=True' in str(result):
            return 1
        else:
            return 0
    except Exception as e:
        return 0

def telegram_bot_sendtext(type_, bot_message):
    
    bot_token = Config().BotTelegramToken
    bot_chatID = Config().BotDepositId if type_ == "deposit" else Config().BotWithdrawId
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()