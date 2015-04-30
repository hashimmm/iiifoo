from lxml import etree


def validate(xml, xsd_filename):
    with open(xsd_filename, 'rb') as schema_file:
        schema_doc = etree.parse(schema_file)
    xmlschema = etree.XMLSchema(schema_doc)
    return xmlschema.validate(xml)


def validate_sitemap(sitemap_xml):
    return validate(sitemap_xml, 'testutils/sitemap.xsd')


def validate_sitemap_index(sitemap_index_xml):
    return validate(sitemap_index_xml, 'testutils/siteindex.xsd')
