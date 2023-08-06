#coding: utf-8
import factory
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from feincms.module.page.models import Page as FeinCMSPage


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User    # Define the related object
    
    # A 'sequential' attribute: each instance of the factory will have a different 'n'
    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.Sequence(lambda n: 'user%s@example.org' % n)
    is_active = True
    is_superuser = False
    is_staff = False
    # password 'test'
    password = 'pbkdf2_sha256$10000$s9Ed0KfEQgTY$CsbbUpXaWk+8eAB+Oga2hBqD82kU4vl+QQaqr/wCZXY='


class SiteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Site
    domain = 'example.com'
    name = 'example.com'
    

class PageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = FeinCMSPage
    
    # TODO: Requires handling of mptt attributes
    # parent must be a Page instance
    parent = None
    level = 0
    title = factory.Sequence(lambda n: 'page %s' % n)
    template_key = 'base'
    tree_id = 1
    active = True
    in_navigation = False
    slug = factory.LazyAttribute(lambda o: slugify(o.title))

