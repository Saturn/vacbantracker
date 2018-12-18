import re

from flask import request, abort
from sqlalchemy import asc, desc

from app.models.profile import Profile
from app.models.tracking import Tracking


def parse_page_query():
    page = request.args.get('page', '1')
    page_regex = re.compile('(\d)')
    page_qs = page_regex.match(page)
    if page_qs:
        page = int(page)
        return page
    return abort(404)


def parse_sort_query():
    sort_col_lookup = {'vac': Profile.vac_banned,
                       'date': Tracking.timetracked,
                       'name': Profile.personaname}
    sort_regex = re.compile('([\+\-])(vac|date|name)')
    sort_col = sort_col_lookup['date']
    sort_order = asc
    sort = request.args.get('sort', '')

    sort_qs = sort_regex.match(sort)
    if sort_qs:
        sort_order = asc if sort_qs.group(1) == '+' else desc
        sort_col = sort_col_lookup[sort_qs.group(2)]
    return sort_order, sort_col
