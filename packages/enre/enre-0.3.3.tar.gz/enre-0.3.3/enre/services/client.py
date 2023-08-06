# -*- coding: utf-8 -*- 

import django.test as test
from django.contrib.auth.models import User


class Client(test.Client):
    pass


class RequestFactory(test.RequestFactory):
    def system(self):
        request = self.post('-system-')
        request.user = User.objects.get(username='system')
        return request

    pass
