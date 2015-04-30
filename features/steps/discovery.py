from behave import *
from lxml import etree

from testutils import sitemap_validator
from source_mappings import source_mapping


@given(u'some defined discoverable source types')
def step_impl(context):
    # source_types = filter(lambda x: source_types[x].discoverable, source_types)
    context.source_types = set([k[0] for k in source_mapping.keys()
                                if source_mapping[k].discoverable])
    assert context.source_types


@when(u'the sitemap index is requested')
def step_impl(context):
    context.response = context.app.get('sitemap_index.xml')


@then(u'a valid sitemap index is returned')
def step_impl(context):
    context.sitemap_index_xml = etree.fromstring(context.response.data)
    assert sitemap_validator.validate_sitemap_index(context.sitemap_index_xml)


@then(u'the response status is 200')
def step_impl(context):
    assert context.response.status_code == 200


@then(u'there must be one sitemap per discoverable source type')
def step_impl(context):
    assert len(context.source_types) == int(context.sitemap_index_xml.xpath(
        'count(//sm:sitemap)',
        namespaces={'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    ))


@when(u'a sitemap is requested')
def step_impl(context):
    assert False


@then(u'a valid sitemap is returned')
def step_impl(context):
    assert False


@given(u'# TODO: finish this.')
def step_impl(context):
    assert False
