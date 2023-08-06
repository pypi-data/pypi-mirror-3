# -*- coding: utf-8 -*- 

def login_required(func):
    setattr(func, 'auth', True)
    return func


def login_exempt(func):
    setattr(func, 'auth', False)
    return func


def permissions_required(*permissions):
    def decorator(func):
        setattr(func, 'permissions', permissions)
        return func

    return decorator
