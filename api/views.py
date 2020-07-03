import base64
import time
import re
import datetime
import random
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from api.util import check_content, is_login
from api.models import *
from django.contrib import auth
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create your views here.


def admin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if check_content(username, password):
        try:
            user = auth.authenticate(username=username, password=base64.b64decode(password)[3:])
        except Exception as e:
            user = None
            print(f'password {password} is invalid, {e}')
        if user:
            if user.is_superuser:
                user_id = user.id
                try:
                    token = Token.objects.filter(user=user).first().key
                except Exception as e:
                    token = None
                    print(f'do not have token, {e}')
                result = {'error_code': 0, 'uid': user_id, 'token': token}
            else:
                result = {'error_code': 10002}
        else:
            result = {'error_code': 10000}
    else:
        result = {'error_code': 10001}

    return JsonResponse(result)


def register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    if check_content(username, password, phone, email):
        if re.match(r'^[a-zA-Z]', username) and len(username) < 11:
            if len(password) < 11:
                rc = re.compile(r'^0\d{2,3}\d{7,8}$|^1[3578]\d{9}$|^147\d{8}')
                if rc.match(phone):
                    rc = re.compile(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')
                    if rc.match(email):
                        if not User.objects.filter(username=username) and not User.objects.filter(email=email) \
                                and not UserDetail.objects.filter(phone=phone):
                            try:
                                user = User.objects.create(username=username, email=email, is_superuser=False, is_staff=True)
                                user.set_password(password)
                                user.save()
                                user_id = user.id
                                UserDetail.objects.create(phone=phone, user=user)
                                Token.objects.create(user=user)
                            except Exception as e:
                                print(f'write to User data failed, {e}')
                                result = {'error_code': 10100}
                            else:
                                result = {'error_code': 0, 'uid': user_id}
                        else:
                            result = {'error_code': 10007}
                    else:
                        result = {'error_code': 10006}
                else:
                    result = {'error_code': 10005}
            else:
                result = {'error_code': 10004}
        else:
            result = {'error_code': 10003}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if check_content(username, password):
        try:
            user = auth.authenticate(username=username, password=base64.b64decode(password)[3:])
        except Exception as e:
            user = None
            print(f'password {password} is invalid, {e}')
        if user:
            user_id = user.id
            try:
                token = Token.objects.filter(user=user).first().key
            except Exception as e:
                token = None
                print(f'do not have token, {e}')
            result = {'error_code': 0, 'uid': user_id, 'token': token}
        else:
            result = {'error_code': 10000}
    else:
        result = {'error_code': 10001}

    return JsonResponse(result)


@is_login
def add_event(request):
    event_title = request.POST.get('title')
    event_limit = request.POST.get('limit')
    event_status = request.POST.get('status')
    event_address = request.POST.get('address')
    event_time = request.POST.get('time')
    event_price = request.POST.get('price')
    event_type = request.POST.get('type')
    # print(event_title, event_address, event_time, event_price, event_type)
    if check_content(event_title, event_address, event_time, event_price, event_type):
        if not Event.objects.filter(title=event_title):
            if len(event_title) <= 20:
                if event_status in ['1', '2', '0']:
                    try:
                        dt = datetime.datetime.strptime(event_time, '%Y-%m-%d %X')
                        if dt.timestamp() - time.time() > 86400:
                            if event_type in ['户外', '文娱', '亲子', '互联网技术', '创业']:
                                uid = request.META.get('HTTP_UID')
                                user = User.objects.filter(id=uid).first()
                                try:
                                    event_add = Event.objects.create(title=event_title,
                                                         limit=int(event_limit),
                                                         status=int(event_status),
                                                         address=event_address,
                                                         time=dt,
                                                         price=int(event_price),
                                                         type=event_type,
                                                         user=user)
                                    result = {'error_code': 0,
                                              'data': {
                                                  'event_id': event_add.id,
                                                  'status': event_status
                                                }
                                              }
                                except Exception as e:
                                    print(f'write to Event data failed, {e}')
                                    result = {'error_code': 10100}
                            else:
                                result = {'error_code': 10015}
                        else:
                            result = {'error_code': 10014}
                    except Exception as e:
                        print(f'time format is wrong, {e}')
                        result = {'error_code': 10013}
                else:
                    result = {'error_code': 10012}
            else:
                result = {'error_code': 10011}
        else:
            result = {'error_code': 10010}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)


@is_login
def get_eventlist(request):
    event_title = request.GET.get('title')
    event_type = request.GET.get('type')
    event_price = request.GET.get('price')
    event_status = request.GET.get('status')
    events = Event.objects.all()
    if event_title not in ['', None]:
        events = events.filter(title__contains=event_title)
    if event_type not in ['', None]:
        events = events.filter(type=event_type)
    if event_price not in ['', None]:
        try:
            event_price = int(event_price)
        except Exception as e:
            print('event_price is not a int, ', e)
            event_price = -1
        events = events.filter(price__lte=event_price)
    if event_status not in ['', None]:
        try:
            event_status = int(event_price)
        except Exception as e:
            print('event_status is not a int, ', e)
            event_status = -1
        events = events.filter(status=int(event_status))
    if events:
        event_list = []
        for e in events:
            event_list.append({'id': e.id, 'title': e.title, 'status': e.status, 'type': e.type, 'price': e.price})
        result = {'event_list': event_list, 'error_code': 0, 'count': len(event_list)}
    else:
        result = {'error_code': 10016}
    return JsonResponse(result)


@is_login
def get_eventdetail(request):
    event_id = request.GET.get('id')
    if check_content(event_id):
        try:
            event_id = int(event_id)
        except:
            event_id = 0
        event_x = Event.objects.filter(id=event_id)
        if event_x:
            event_x = event_x.first()
            event_detail = {'id': str(event_x.id), 'title':event_x.title, 'status': event_x.status,
                            'limit': event_x.limit, 'address': event_x.address, 'start_time': event_x.time,
                            'type': event_x.type, 'price': event_x.price}
            result = {'event_detail':event_detail, 'error_code': 0}
        else:
            result = {'error_code': 10017}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)

@is_login
def order(request):
    event_id = request.POST.get('eid')
    counts = request.POST.get('count')
    # print(counts)
    if not counts:
        counts = 1
    try:
        counts = int(counts)
    except Exception as e:
        print(f'counts is a error para, {e}')
        result = {'error_code': 10100}
    else:
        if check_content(event_id):
            try:
                event_id = int(event_id)
            except Exception as e:
                print(f'event_id is a error para, {e}')
                result = {'error_code': 10017}
            else:
                event_x = Event.objects.filter(id = event_id)
                if event_x:
                    event_x = event_x.first()
                    uid = request.META.get('HTTP_UID')
                    user = User.objects.filter(id=uid).first()
                    # print(event_x.status)
                    if event_x.status != 2:
                        print(type(event_x.time))
                        print(event_x.time)
                        if event_x.time.timestamp() - time.time() >0:
                            all_num = event_x.limit
                            order_list = Order.objects.filter(event=event_x)
                            if order_list:
                                ordered_num = sum(orders.count for orders in order_list)
                            else:
                                ordered_num = 0
                            if all_num - ordered_num > counts:
                                order_code = time.strftime('%Y%m%d%H%M%S',time.localtime()) + str(random.randint(1000,9999))
                                Order.objects.create(order_code=order_code, count=counts, user=user, event=event_x)
                                result = {'error_code': 0, 'order_code': order_code}
                            else:
                                result = {'error_code': 10020}
                        else:
                            result = {'error_code': 10018}
                    else:
                        result = {'error_code': 10019}
                else:
                    result = {'error_code': 10017}
        else:
            result = {'error_code': 10001}
    return JsonResponse(result)


def pay(request):
    oid = request.POST.get('oid')
    pay_type = request.POST.get('pay_type')
    # print(oid)
    if not check_content(pay_type):
        pay_type = 0
    if check_content(oid):
        uid = request.META.get('HTTP_UID')
        user = User.objects.filter(id=uid).first()
        # print(user)
        my_order = Order.objects.filter(user=user, order_code=oid)
        if my_order:
            my_order = my_order.first()
            if my_order.ispay != 1:
                if my_order.ispay == 0:
                    if pay_type == 0:
                        print('zhifubao pay!')
                        pay_interface = 'zhifubao'
                    elif pay_type == 1:
                        print('weixin pay!')
                        pay_interface = 'weixin'
                    else:
                        print('yinlian pay!')
                        pay_interface = 'yinlian'
                    is_pay = pay_interface
                    if is_pay:
                        print('pay success!')
                        order_count = my_order.count
                        order_id = random.randint(100000000, 999999999)
                        tickets_list = list(ids for ids in range(order_id, order_id+order_count))
                        my_order.ispay = 1
                        my_order.save()
                        for ticket in tickets_list:
                            Tickets.objects.create(ticket_id=ticket, order=my_order)
                        result = {'error_code': 0,
                                  'data': {
                                    'oid': oid,
                                    'tickets': tickets_list
                                    }}
                    else:
                        print('pay info is invalid')
                        result = {'error_code': 10100}
                else:
                    print('order is abnormal!')
                    result = {'error_code': 10100}
            else:
                print('order is payed!')
                result = {'error_code': 10100}
        else:
            print('order code is invalid')
            result = {'error_code': 10100}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)


@is_login
def sign(request):
    uid = request.POST.get('uid')
    phone_number = request.POST.get('phone_number')
    ticket_id = request.POST.get('ticket_id')
    if check_content(uid, phone_number, ticket_id):
        user = User.objects.filter(id=uid).first()
        user_phone = UserDetail.objects.filter(user=user).first().phone
        # print(user_phone)
        if user_phone == phone_number:
            try:
                ticket = Tickets.objects.filter(ticket_id=ticket_id).first()
                print(ticket)
                assert ticket is not None, 'ticket is not null'
            except Exception as e:
                print(f'ticket invalid, {e}')
                result = {'error_code': 10100}
            else:
                if ticket.order.user == user:
                    result = {'error_code': 0}
                else:
                    print('User and ticket do not match')
                    result = {'error_code': 10100}
        else:
            print('User and phone_number do not match')
            result = {'error_code': 10100}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)