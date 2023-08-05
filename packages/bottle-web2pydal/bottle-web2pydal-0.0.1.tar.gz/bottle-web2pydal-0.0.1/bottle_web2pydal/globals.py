#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

current = threading.local()  # thread-local storage for request-scope globals


def T(text):
    """ Fake T """
    return text
