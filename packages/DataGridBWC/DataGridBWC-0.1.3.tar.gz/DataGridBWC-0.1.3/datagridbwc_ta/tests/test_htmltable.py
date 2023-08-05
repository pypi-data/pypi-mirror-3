import difflib

from blazeweb.routing import Rule
from blazeweb.testing import inrequest
from nose.tools import eq_

from datagridbwc.lib.htmltable import Table, Col, A

def eq_or_diff(actual, expected):
    assert actual == expected, \
    '\n'.join(list(
        difflib.unified_diff(actual.split('\n'), expected.split('\n'))
    ))

def test_basic():
    data = (
        {'color': 'red', 'number': 1},
        {'color': 'green', 'number': 2},
        {'color': 'blue', 'number': 3},
    )
    t = Table()
    t.color = Col('Color')
    t.number = Col('Number')
    result = """<table cellpadding="0" cellspacing="0" summary="">
    <thead>
        <tr>
            <th>Color</th>
            <th>Number</th>
        </tr>
    </thead>
    <tbody>
        <tr class="odd">
            <td>red</td>
            <td>1</td>
        </tr>
        <tr class="even">
            <td>green</td>
            <td>2</td>
        </tr>
        <tr class="odd">
            <td>blue</td>
            <td>3</td>
        </tr>
    </tbody>
</table>"""
    eq_(result, t.render(data))

def test_row_dec():
    data = (
        {'color': 'red', 'number': 1},
        {'color': 'green', 'number': 2},
        {'color': 'blue', 'number': 3},
    )
    def row_decorator(row_num, row_attrs, row):
        if row_num % 2 == 0:
            row_attrs.add_attr('class', 'ceven')
        else:
            row_attrs.add_attr('class', 'codd')
        row_attrs.add_attr('class', row['color'])
    t = Table(row_dec = row_decorator)
    t.color = Col('Color')
    t.number = Col('Number')
    result = """<table cellpadding="0" cellspacing="0" summary="">
    <thead>
        <tr>
            <th>Color</th>
            <th>Number</th>
        </tr>
    </thead>
    <tbody>
        <tr class="odd codd red">
            <td>red</td>
            <td>1</td>
        </tr>
        <tr class="even ceven green">
            <td>green</td>
            <td>2</td>
        </tr>
        <tr class="odd codd blue">
            <td>blue</td>
            <td>3</td>
        </tr>
    </tbody>
</table>"""
    eq_or_diff(result, t.render(data))


class TestA(object):

    @inrequest()
    def test_links(self):
        dbobj_fake = {'arg1': 1, 'arg2': 2, 'db1': 10, 'db2': 20, 'title': 'fake_object'}
        dummy_col = Col('test')
        dummy_col.crow = dbobj_fake

        a1 = A('mod:Index', 'arg1:db1', 'arg2', label='split', class_='name_split', title='Different names for arg and field')
        a2 = A('mod:Index', 'arg1', 'arg2:db2', class_='name_single', title='Same names for arg and field')

        eq_(a1.process('title',dummy_col.extract), '<a class="name_split" href="/index/10/2" title="Different names for arg and field">split</a>')
        eq_(a2.process('title',dummy_col.extract), '<a class="name_single" href="/index/1/20" title="Same names for arg and field">fake_object</a>')
