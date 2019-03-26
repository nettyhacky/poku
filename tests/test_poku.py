#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `poku` package."""

from unittest.mock import Mock, patch
import pytest

import configargparse

from poku import poku, pocket


@pytest.fixture
def mandatory_args():
    return [
        '--consumer', 'abc'
    ]


def test_parse_consumer(mandatory_args):
    """ Test that a consumer argument is handled and received """
    args = poku.parse_args(mandatory_args + ['--consumer', 'def'])
    assert args.consumer == 'def'


def test_parse_access_token(mandatory_args):
    """ Test that an access token argument is handled and received """
    args = poku.parse_args(mandatory_args + ['--access', 'ghi'])
    assert args.access == 'ghi'


def test_no_consumer():
    """ Test that missing out the consumer argument causes a system exit """
    with pytest.raises(SystemExit):
        args = poku.parse_args([])


@patch('poku.poku.requests.post')
def test_get_request_token(mock_get):
    """ Test if successful token requests return expected token """
    mock_get.return_value.ok = True
    mock_get.return_value.json = lambda: {'code': 'b'}

    token = pocket.get_pocket_request_token('abc')
    assert token == 'b'


@patch('poku.poku.requests.post')
def test_get_request_token_not_ok(mock_get):
    """ Test that unsuccessful token requests return None """
    mock_get.return_value.ok = False

    token = pocket.get_pocket_request_token('abc')
    assert token is None


def test_generate_auth_url():
    """ test that expected auth url is generated """
    token = 'hello'
    expected_url = ('https://getpocket.com/auth/authorize'
                    '?request_token={0}'
                    '&redirect_uri=https://getpocket.com').format(token)

    url = pocket.generate_pocket_auth_url(token)
    assert url == expected_url


@patch('poku.poku.requests.post')
def test_get_access_token(mock_get):
    """ test access token requests """
    mock_get.return_value.ok = True
    mock_get.return_value.json = lambda: {'access_token': 'a'}

    atoken = pocket.get_pocket_access_token('ck', 'rt')
    assert atoken == 'a'


@patch('poku.poku.requests.post')
def test_get_access_token_not_ok(mock_get):
    """ test that unsuccessful access token requests return None """
    mock_get.return_value.ok = False

    atoken = pocket.get_pocket_access_token('ck', 'rt')
    assert atoken is None


@patch('poku.poku.requests.post')
def test_get_pocket_items(mock_get):
    """ test that pocket items requests returns expected list """
    mock_get.return_value.ok = True
    mock_get.return_value.json = lambda: {'list': {'a': 'test1', 'b': 'test2'}}
    expected = ['test1', 'test2']

    pocket_items = sorted(pocket.get_pocket_items('ck', 'at'))
    assert pocket_items == expected


@patch('poku.poku.requests.post')
def test_get_pocket_items_not_ok(mock_get):
    """ test that unsuccessful pocket items requests return None """
    mock_get.return_value.ok = False

    pocket_items = pocket.get_pocket_items('ck', 'at')
    assert pocket_items is None


def test_pocket_item_to_dict():
    """ test converting of pocket item to universal item """
    pocket_item = {
        'resolved_url': 'test.com',
        'resolved_title': 'test page',
        'tags': {'test': {}, 'test2': {}},
        'time_updated': '1'
    }
    expected = {
        'url': 'test.com',
        'title': 'test page',
        'tags': ['test', 'test2'],
        'timestamp': 1
    }

    dict_item = pocket.pocket_item_to_dict(pocket_item)
    assert dict_item == expected


def test_buku_item_to_dict():
    """ test converting of buku item to universal item """
    buku_item = (1, 'test.com', 'test page', ',test,test2,')
    expected = {
        'url': 'test.com',
        'title': 'test page',
        'tags': ['test', 'test2'],
        'timestamp': 1
    }

    dict_item = poku.buku_item_to_dict(buku_item)
    assert dict_item == expected


@pytest.mark.parametrize('item_list', [
    [{'timestamp': '1'}, {'timestamp': '2'}],
    [{'timestamp': '2'}, {'timestamp': '1'}]
])
def test_sort_dict_items(item_list):
    """ test that items are being sorted correctly """
    expected = [{'timestamp': '1'}, {'timestamp': '2'}]
    sorted_list = poku.sort_dict_items(item_list)

    assert sorted_list == expected


def test_dict_list_difference():
    """ test return of items in list1 but not in list2 """
    l1 = [{'url': 'a'}, {'url': 'b'}, {'url': 'c'}]
    l2 = [{'url': 'b'}, {'url': 'c'}]
    expected = [{'url': 'a'}]

    filtered_list = poku.dict_list_difference(l1, l2)
    assert filtered_list == expected
