from unittest.mock import patch

import json
import pytest
import pprint

from chalice.test import Client

from app import app


def test_scrapeposts_normal():
    with Client(app) as scraper_app:
        resources = ['arn:aws:lambda:us-west-2:342504367174:rule/ExampleRule']
        events = scraper_app.events.generate_cw_event('Scheduled Event', 'aws.events', {}, resources)
        scraper_app.lambda_.invoke('scrape_posts', events)
