"""
my util py
"""
from api.util import *
import pytest
from time import sleep


@pytest.mark.parametrize('a', ['a'])
@pytest.mark.parametrize('b', ['b', 0, None, ''])
def test_check_content(a, b):
    print(f'a is {a}, b is {b}')
    sleep(1)
    if b in ['', None]:
        print('bbbbbbbbbbbbb')
        assert not check_content(a, b)
    else:
        assert check_content(a, b)


if __name__ == '__main__':
    pytest.main(['-v', '-s'])
