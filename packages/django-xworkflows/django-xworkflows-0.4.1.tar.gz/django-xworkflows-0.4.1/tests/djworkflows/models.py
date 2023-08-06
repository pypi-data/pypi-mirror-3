# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Raphaël Barrois

from django.db import models

from django_xworkflows import models as dxmodels

class MyWorkflow(dxmodels.Workflow):
    states = (
        ('foo', u"Foo"),
        ('bar', u"Bar"),
        ('baz', u"Baz"),
    )
    transitions = (
        ('foobar', 'foo', 'bar'),
        ('gobaz', ('foo', 'bar'), 'baz'),
        ('bazbar', 'baz', 'bar'),
    )
    initial_state = 'foo'


class MyAltWorkflow(dxmodels.Workflow):
    states = (
        ('a', 'StateA'),
        ('b', 'StateB'),
        ('c', 'StateC'),
    )
    transitions = (
        ('tob', ('a', 'c'), 'b'),
        ('toa', ('b', 'c'), 'a'),
        ('toc', ('a', 'b'), 'c'),
    )
    initial_state = 'a'

    log_model = ''


class MyWorkflowEnabled(dxmodels.WorkflowEnabled, models.Model):
    OTHER_CHOICES = (
        ('aaa', u"AAA"),
        ('bbb', u"BBB"),
    )

    state = dxmodels.StateField(MyWorkflow)
    other = models.CharField(max_length=4, choices=OTHER_CHOICES)

    def fail_if_fortytwo(self, res, *args, **kwargs):
        if res == 42:
            raise ValueError()

    @dxmodels.transition(after=fail_if_fortytwo)
    def gobaz(self, foo):
        return foo * 2


class WithTwoWorkflows(dxmodels.WorkflowEnabled, models.Model):
    state1 = dxmodels.StateField(MyWorkflow())
    state2 = dxmodels.StateField(MyAltWorkflow())
