# coding: utf8
"""
    weasyprint.html
    ---------------

    Specific handling for some HTML elements, especially replaced elements.

    Replaced elements (eg. <img> elements) are rendered externally and
    behave as an atomic opaque box in CSS. In general, they may or may not
    have intrinsic dimensions. But the only replaced elements currently
    supported in WeasyPrint are images with intrinsic dimensions.

    :copyright: Copyright 2011-2012 Simon Sapin and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

from .formatting_structure import boxes
from .utils import get_url_attribute
from .compat import xrange


# Maps HTML tag names to function taking an HTML element and returning a Box.
HTML_HANDLERS = {}


def handle_element(document, element, box):
    """Handle HTML elements that need special care.

    :returns: a (possibly empty) list of boxes.
    """
    if box.element_tag in HTML_HANDLERS:
        return HTML_HANDLERS[element.tag](document, element, box)
    else:
        return [box]


def handler(tag):
    """Return a decorator registering a function handling ``tag`` elements."""
    def decorator(function):
        """Decorator registering a function handling ``tag`` elements."""
        HTML_HANDLERS[tag] = function
        return function
    return decorator


def make_replaced_box(element, box, image):
    """Wrap an image in a replaced box.

    That box is either block-level or inline-level, depending on what the
    element should be.

    """
    if box.style.display in ('block', 'list-item', 'table'):
        type_ = boxes.BlockReplacedBox
    else:
        # TODO: support images with 'display: table-cell'?
        type_ = boxes.InlineReplacedBox
    return type_(element.tag, element.sourceline, box.style, image)


@handler('img')
def handle_img(document, element, box):
    """Handle ``<img>`` elements, return either an image or the alt-text.

    See: http://www.w3.org/TR/html5/embedded-content-1.html#the-img-element

    """
    src = get_url_attribute(element, 'src')
    alt = element.get('alt')
    if src:
        image = document.get_image_from_uri(src)
        if image is not None:
            return [make_replaced_box(element, box, image)]
        else:
            # Invalid image, use the alt-text.
            if alt:
                return [box.copy_with_children(
                    [boxes.TextBox.anonymous_from(box, alt)])]
            elif alt == '':
                # The element represents nothing
                return []
            else:
                assert alt is None
                # TODO: find some indicator that an image is missing.
                # For now, just remove the image.
                return []
    else:
        if alt:
            return [box.copy_with_children(
                [boxes.TextBox.anonymous_from(box, alt)])]
        else:
            return []


@handler('embed')
def handle_embed(document, element, box):
    """Handle ``<embed>`` elements, return either an image or nothing.

    See: http://www.w3.org/TR/html5/the-iframe-element.html#the-embed-element

    """
    src = get_url_attribute(element, 'src')
    type_ = element.get('type', '').strip()
    if src:
        image = document.get_image_from_uri(src, type_)
        if image is not None:
            return [make_replaced_box(element, box, image)]
    # No fallback.
    return []


@handler('object')
def handle_object(document, element, box):
    """Handle ``<object>`` elements, return either an image or the fallback
    content.

    See: http://www.w3.org/TR/html5/the-iframe-element.html#the-object-element

    """
    data = get_url_attribute(element, 'data')
    type_ = element.get('type', '').strip()
    if data:
        image = document.get_image_from_uri(data, type_)
        if image is not None:
            return [make_replaced_box(element, box, image)]
    # The element’s children are the fallback.
    return [box]


def integer_attribute(element, box, name, minimum=1):
    """Read an integer attribute from the HTML element and set it on the box.

    """
    value = element.get(name, '').strip()
    if value:
        try:
            value = int(value)
        except ValueError:
            pass
        else:
            if value >= minimum:
                setattr(box, name, value)


@handler('colgroup')
def handle_colgroup(_document, element, box):
    """Handle the ``span`` attribute."""
    if isinstance(box, boxes.TableColumnGroupBox):
        if any(child.tag == 'col' for child in element):
            box.span = None  # sum of the children’s spans
        else:
            integer_attribute(element, box, 'span')
            box.children = (
                boxes.TableColumnBox.anonymous_from(box, [])
                for _i in xrange(box.span))
    return [box]


@handler('col')
def handle_col(_document, element, box):
    """Handle the ``span`` attribute."""
    if isinstance(box, boxes.TableColumnBox):
        integer_attribute(element, box, 'span')
        if box.span > 1:
            # Generate multiple boxes
            # http://lists.w3.org/Archives/Public/www-style/2011Nov/0293.html
            return [box.copy() for _i in xrange(box.span)]
    return [box]


@handler('th')
@handler('td')
def handle_td(_document, element, box):
    """Handle the ``colspan``, ``rowspan`` attributes."""
    if isinstance(box, boxes.TableCellBox):
        # HTML 4.01 gives special meaning to colspan=0
        # http://www.w3.org/TR/html401/struct/tables.html#adef-rowspan
        # but HTML 5 removed it
        # http://www.w3.org/TR/html5/tabular-data.html#attr-tdth-colspan
        # rowspan=0 is still there though.
        integer_attribute(element, box, 'colspan')
        integer_attribute(element, box, 'rowspan', minimum=0)
    return [box]
