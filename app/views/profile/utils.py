import re
from flask import request, abort


def parse_page_query():
    page = request.args.get('page', '1')
    page_regex = re.compile('(\d)')
    page_qs = page_regex.match(page)
    if page_qs:
        page = int(page)
        return page
    return abort(404)


def parse_sort_query():
    sort = request.args.get('sort', '')
    direction = request.args.get('direction', 'desc')
    if not direction.lower() in ('asc', 'desc'):
        direction = 'desc'
    if sort.lower() in ('name', 'date', 'vac'):
        return sort, direction


def get_tracking_sort_by_urls(direction, sort_by):
    """
    Args:
        direction - string, either 'asc' or 'desc'
        sort_by - column name to sort by
    Returns:
        dict with keys for name and value is the url
    """
    urls = {}
    base = '/tracking?sort={}&direction={}'
    urls['date'] = base.format('date', 'desc')
    urls['name'] = base.format('name', 'desc')
    urls['vac'] = base.format('vac', 'desc')

    # flip the direction (for currently selected sorting column)
    new_direction = 'asc' if direction == 'desc' else 'desc'
    urls[sort_by] = base.format(sort_by, new_direction)

    return urls
