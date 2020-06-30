"""
my util py
"""
import hashlib
import time
from functools import wraps
from django.http import JsonResponse
from rest_framework.authtoken.models import Token


def check_content(*args):
    return all(map(lambda x: x not in ['', None], args))


def get_token_code(username):
    timestamp = str(time.time())
    m = hashlib.md5()


def is_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        uid = request.META.get('HTTP_UID')
        key = request.META.get('HTTP_KEY')
        if request.method == 'POST':
            rstr = request.POST.get('rstr')
        else:
            rstr = request.GET.get('rstr')
        if check_content(uid, key, rstr):
            try:
                token = Token.objects.filter(user_id = int(uid)).first().key
            except Exception as e:
                print(f'get token error, {e}')
                return JsonResponse({"error": 10008})
            md5 = hashlib.md5()
            md5.update((uid + rstr + token).encode('utf-8'))
            key_a = md5.hexdigest()
            # print(key_a)
            if key_a == key:
                return func(*args, **kwargs)
            else:
                return JsonResponse({"error": 10008})
        else:
            return JsonResponse({"error": 10001})
    return wrapper


if __name__ == '__main__':
    print(check_content('a','b'))
    print(check_content('a', ''))
    print(check_content('a', None))
    print(check_content('a', 0))