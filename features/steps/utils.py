from time import time
from behave import *
from caching import cached


@given(u'a cached method that returns current time')
def step_impl(context):
    @cached(timeout=5)
    def curtime():
        return time()
    context.timefunc = curtime


@when(u'it is called twice')
def step_impl(context):
    context.time1 = context.timefunc()
    context.time2 = context.timefunc()


@then(u'the same time is returned')
def step_impl(context):
    assert context.time1 == context.time2
