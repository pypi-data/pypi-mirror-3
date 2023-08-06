#coding: utf-8
from django.db import IntegrityError
from django.contrib.sites.models import Site

from .factories import ( UserFactory, PageFactory,
    SiteFactory)

def make_users(users=1, staff=0):
    """ Create a bunch of users and the admin. """
    # First, the admin
    UserFactory(
        username='admin',
        email='admin@example.org',
        is_superuser=True,
        is_staff=True
    )
    # then the regular users
    for user in xrange(users):
        UserFactory()
    # create staff users
    for user in xrange(staff):
        UserFactory(is_staff=True)
    

def example_site():
    """ Create the site 'example.com' """
    try:
        site = SiteFactory()
    except IntegrityError:
        site = Site.objects.get(domain='example.com')
    return site

def basic_page_structure():
    """ Create a root page and a sub-page """
    page1 = PageFactory(title='Test page',
                slug='test-page',
                site_id=1,
                lft=1,
                rght=4
                )
    PageFactory(title='Test child page',
                slug='test-child-page',
                site_id=1,
                parent=page1,
                level=1,
                lft=2,
                rght=3)
    

