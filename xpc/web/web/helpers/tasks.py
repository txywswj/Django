from celery import Celery
import requests
SMS_API = 'http://sms-api.luosimao.com/v1/send.json'
SMS_USER = 'api'
SMS_KEY = 'd4c73a2afa7864d061e8d8e9a11a5f19'
SMS_API_AUTH = (SMS_USER, 'key-%s' % SMS_KEY)

app =Celery('tasks',broker='redis://127.0.0.1')



@app.task
def send_sms_code(phone, code):
    message = '您的验证码是：%s，请在收到后的10分钟内输入。【千锋】' % code
    requests.post(SMS_API, data={
        'mobile': phone,
        'message': message
    }, auth=SMS_API_AUTH)
    print('send sms to %s: %s' % (phone, message))