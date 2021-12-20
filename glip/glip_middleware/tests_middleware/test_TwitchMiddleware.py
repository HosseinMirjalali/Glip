#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TwitchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print(f"view name: {view_func.__name__}")
        pass
