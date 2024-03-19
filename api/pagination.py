from collections import OrderedDict
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param
import math


class HeaderLimitOffsetPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.use_envelope = False
        if str(request.GET.get('envelope')).lower() in ['true', 1]:
            self.use_envelope = True
        return super().paginate_queryset(queryset, request, view)

    def get_first_link(self):
        if self.offset <= 0:
            return None
        url = self.request.build_absolute_uri()
        return remove_query_param(url, self.offset_query_param)

    def get_last_link(self):
        if self.offset + self.limit >= self.count:
            return None
        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)
        offset = self.count - self.limit
        return replace_query_param(url, self.offset_query_param, offset)

    def get_total_pages(self):
        return math.ceil(self.count / self.limit)

    def get_current_page(self):
        if self.offset <= 0:
            return 1
        return int((self.offset / self.limit) + 1)

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        first_url = self.get_first_link()
        last_url = self.get_last_link()
        total_pages = self.get_total_pages()
        current_page = self.get_current_page()

        links = []
        for label, url in (
                ('first', first_url),
                ('next', next_url),
                ('previous', previous_url),
                ('last', last_url)):
            if url is not None:
                links.append(f'<{url}>; rel="{label}"')

        headers = {"Link": ", ".join(links)} if links else {}

        if self.use_envelope:
            return Response(
                OrderedDict(
                    [
                        ('count', self.count),
                        ('total_pages', total_pages),
                        ('current_page', current_page),
                        ('first', first_url),
                        ('next', next_url),
                        ('previous', previous_url),
                        ('last', last_url),
                        ('results', data),
                    ]
                ),
                headers=headers,
            )
        return Response(data, headers=headers)