from datetime import datetime
from django.http import JsonResponse
from web.helpers.code import gen_code, verify
from web.helpers.tasks import send_sms_code
from web.models.codes import Code
from web.models.composer import Composer
from web.helpers.composer import get_posts_by_cid, md5_pwd
from django.shortcuts import render
from web.models.copyright import Copyright


def oneuser(request, cid):
    composer = Composer.objects.get(cid=cid)
    cr_list = Copyright.objects.filter(cid=cid)[:2]
    composer.posts = get_posts_by_cid(cid)
    return render(request, 'oneuser.html', locals())


def homepage(request, cid):
    composer = Composer.objects.get(cid=cid)
    cr_list = Copyright.objects.filter(cid=cid).all()
    composer.posts = get_posts_by_cid(cid)

    return render(request, 'homepage.html', locals())


def do_register(request):
    nickname = request.POST.get('nickname')
    phone = request.POST.get('phone')
    code = request.POST.get('code')
    password = request.POST.get('password')
    prefix_code = request.POST.get('prefix_code')
    callback = request.POST.get('callback')
    if Composer.objects.filter(phone=phone).exists():
        data = {'status': -1025, 'msg': '该手机号被注册过了'}
        return JsonResponse(data)
    if not verify(phone, code):
        return JsonResponse({"status": -1, "msg": "手机验证失败"})
    composer = Composer()
    composer.name = nickname
    composer.cid = composer.phone = phone
    composer.password = md5_pwd(phone,password)
    composer.avatar = ''
    composer.banner = ''
    composer.save()
    return JsonResponse({
        'status': 0,
        'data:{'
        'callback': '/'
    } )


def register(request):
    return render(request, 'register.html')



def send_code(request):
    prefix_code = request.POST.get('prefix_code')
    phone = request.POST.get('phone')
    composer = Composer.get_by_phone(phone)
    if composer:
        return JsonResponse({"status":-1025,"msg":"该手机号已注册过"})
    code = Code()
    code.phone = phone
    code.code = gen_code()
    code.ip = request.META['REMOTE_ADDR']
    code.created_at = datetime.now()
    code.save()
    send_sms_code.delay(phone, code.code)
    return JsonResponse({
        "status": 0,
        "msg": "OK",
        "data": {
            "phone": phone,
            "prefix_code": prefix_code,
        }})

def login(request):
    return render(request, 'login.html')


# def do_login(request):
#     phone = request.POST.get('value')
#     password = request.POST.get('password')
#     composer = Composer.objects.filter(phone=phone).first()
#     if not composer or composer.password != password:
#         return JsonResponse({'status': -1, 'msg': '用户名或密码错误'})
#     return JsonResponse({
#         'status': 0,
#         'data': {
#             'callack': '/'
#         }
#     })
def do_login(request):
    phone =request.POST.get('value')
    password=request.POST.get('password')
    composer=Composer.objects.filter(phone=phone).first()
    if not composer or composer.password!=password:
        return  JsonResponse({'status':1,'msg':'用户名或者密码错误'})
    return JsonResponse({
        'status':0,
        'data':{
            'callback':'/'
        }
    })

def find_password():
    return None