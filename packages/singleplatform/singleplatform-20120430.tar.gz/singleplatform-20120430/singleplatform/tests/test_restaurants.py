#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis
import logging; log = logging.getLogger(__name__)

from . import BaseEnpdointTestCase



class RestaurantsEndpointTestCase(BaseEnpdointTestCase):
    def test_search(self):
        response = self.api.restaurants.search({
            'q': 'New York, NY',
        })
        assert response.get('ok') is True
        assert 'results' in response

    def test_location(self):
        response = self.api.restaurants.location(self.default_locationid)
        assert 'id' in response

    def test_menu(self):
        response = self.api.restaurants.menu(self.default_locationid)
        assert 'location' in response
        assert 'menus' in response

    def test_shortmenu(self):
        response = self.api.restaurants.shortmenu(self.default_locationid)
        assert 'type' in response
        assert 'location' in response
        assert 'shortMenu' in response
