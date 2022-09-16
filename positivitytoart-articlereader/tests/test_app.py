
from chalice.test import Client

from app import app


def test_readarticles_normal():
    with Client(app) as scraper_app:
        resources = ['arn:aws:lambda:us-west-2:342504367174:rule/ExampleRule']
        events = scraper_app.events.generate_cw_event('Scheduled Event', 'aws.events', {}, resources)
        scraper_app.lambda_.invoke('read_articles', events)
