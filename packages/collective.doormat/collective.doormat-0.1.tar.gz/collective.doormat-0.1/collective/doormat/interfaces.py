from zope import interface, schema
from plone.theme.interfaces import IDefaultPloneLayer

from collective.doormat import doormatMessageFactory as _


class IDoormatLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IDoormatSettingsSchema(interface.Interface):

    enabled_sections = schema.List(
        title=_(u'Sections'),
        description=_(u'Sections to display and order'),
        required=False,
        readonly=False,
        default=[],
        value_type = schema.Choice( title=_(u"Enabled sections"),
                source="collective.doormat.sections"
                )
        )



    doormat_header = schema.Text(
        title=u'Header',
        description=u'Text above doormat',
        required=False,
        readonly=False,
        default=None,
        )


    section1_title = schema.TextLine(
        title=u'Section 1 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section1_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )


    section1_text = schema.Text(
        title=u'Section 1 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section2_title = schema.TextLine(
        title=u'Section 2 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section2_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section2_text = schema.Text(
        title=u'Section 2 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section3_title = schema.TextLine(
        title=u'Section 3 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section3_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section3_text = schema.Text(
        title=u'Section 3 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section4_title = schema.TextLine(
        title=u'Section 4 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section4_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section4_text = schema.Text(
        title=u'Section 4 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section5_title = schema.TextLine(
        title=u'Section 5 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section5_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )


    section5_text = schema.Text(
        title=u'Section 5 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section6_title = schema.TextLine(
        title=u'Section 6 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section6_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )


    section6_text = schema.Text(
        title=u'Section 6 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section7_title = schema.TextLine(
        title=u'Section 7 title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section7_link = schema.TextLine(
        title=u'Link target for title',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    section7_text = schema.Text(
        title=u'Section 7 body',
        description=u'',
        required=False,
        readonly=False,
        default=None,
        )

    doormat_footer = schema.Text(
        title=u'Footer',
        description=u'Text below doormat',
        required=False,
        readonly=False,
        default=None,
        )
