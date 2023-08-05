#!/usr/bin/python3.2
from os import kill
from mock import Mock, sentinel, patch

mock = Mock(return_value=2)
#mock.return_value = sentinel.ret

@patch("kill", mock)
def test():
    return kill(1084, 0)

ret = test()
mock.assert_called_with(1084, 0)
assert ret == 3, "incorrect return value"
print(ret)
