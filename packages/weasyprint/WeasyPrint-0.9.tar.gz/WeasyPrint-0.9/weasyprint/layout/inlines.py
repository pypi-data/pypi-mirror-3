# coding: utf8
"""
    weasyprint.layout.inline
    ------------------------

    Line breaking and layout for inline-level boxes.

    :copyright: Copyright 2011-2012 Simon Sapin and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals
import functools

import cairo

from .absolute import absolute_layout, AbsolutePlaceholder
from .markers import image_marker_layout
from .percentages import resolve_percentages, resolve_one_percentage
from .preferred import shrink_to_fit
from .tables import find_in_flow_baseline, table_wrapper_width
from ..text import TextFragment
from ..formatting_structure import boxes
from ..css.computed_values import used_line_height


def iter_line_boxes(document, box, position_y, skip_stack,
                    containing_block, device_size, absolute_boxes):
    """Return an iterator of ``(line, resume_at)``.

    ``line`` is a laid-out LineBox with as much content as possible that
    fits in the available width.

    :param linebox: a non-laid-out :class:`LineBox`
    :param position_y: vertical top position of the line box on the page
    :param skip_stack: ``None`` to start at the beginning of ``linebox``,
                       or a ``resume_at`` value to continue just after an
                       already laid-out line.
    :param containing_block: Containing block of the line box:
                             a :class:`BlockContainerBox`
    :param device_size: ``(width, height)`` of the current page.

    """
    strut = used_line_height(containing_block.style)
    while 1:
        line, resume_at = get_next_linebox(
            document, box, position_y, skip_stack,
            containing_block, device_size, absolute_boxes)
        if line is None:
            return
        # TODO: Make sure the line and the strut are on the same baseline.
        # See http://www.w3.org/TR/CSS21/visudet.html#line-height
        line.height = max(line.height, strut)
        yield line, resume_at
        if resume_at is None:
            return
        skip_stack = resume_at
        position_y += line.height


def get_next_linebox(document, linebox, position_y, skip_stack,
                     containing_block, device_size, absolute_boxes):
    """Return ``(line, resume_at)``."""
    position_x = linebox.position_x
    linebox.position_y = position_y
    max_x = position_x + containing_block.width
    if skip_stack is None:
        # text-indent only at the start of the first line
        # Other percentages (margins, width, ...) do not apply.
        resolve_one_percentage(linebox, 'text_indent', containing_block.width)
        position_x += linebox.text_indent

    skip_stack = skip_first_whitespace(linebox, skip_stack)
    if skip_stack == 'continue':
        return None, None

    line_placeholders = []

    resolve_percentages(linebox, containing_block)
    line, resume_at, preserved_line_break = split_inline_box(
        document, linebox, position_x, max_x, skip_stack, containing_block,
        device_size, absolute_boxes, line_placeholders)

    remove_last_whitespace(document, line)

    bottom, top = inline_box_verticality(line, baseline_y=0)
    last = resume_at is None or preserved_line_break
    offset_x = text_align(document, line, containing_block, last)
    if bottom is None:
        # No children at all
        line.position_y = position_y
        offset_y = 0
        if preserved_line_break:
            # Only the strut.
            line.baseline = line.margin_top
            line.height += line.margin_top + line.margin_bottom
        else:
            line.height = 0
            line.baseline = 0
    else:
        assert top is not None
        line.baseline = -top
        line.position_y = top
        line.height = bottom - top
        offset_y = position_y - top
    line.margin_top = 0
    line.margin_bottom = 0
    if offset_x != 0 or offset_y != 0:
        # This also translates children
        line.translate(offset_x, offset_y)

    for placeholder in line_placeholders:
        if placeholder.style._weasy_specified_display.startswith('inline'):
            # Inline-level static position:
            placeholder.translate(0, position_y - placeholder.position_y)
        else:
            # Block-level static position: at the start of the next line
            placeholder.translate(
                line.position_x - placeholder.position_x,
                position_y + line.height - placeholder.position_y)

    return line, resume_at


def skip_first_whitespace(box, skip_stack):
    """Return the ``skip_stack`` to start just after the remove spaces
    at the beginning of the line.

    See http://www.w3.org/TR/CSS21/text.html#white-space-model
    """
    if skip_stack is None:
        index = 0
        next_skip_stack = None
    else:
        index, next_skip_stack = skip_stack

    if isinstance(box, boxes.TextBox):
        assert next_skip_stack is None
        white_space = box.style.white_space
        length = len(box.text)
        if index == length:
            # Starting a the end of the TextBox, no text to see: Continue
            return 'continue'
        if white_space in ('normal', 'nowrap', 'pre-line'):
            while index < length and box.text[index] == ' ':
                index += 1
        return index, None

    if isinstance(box, (boxes.LineBox, boxes.InlineBox)):
        if index == 0 and not box.children:
            return None
        result = skip_first_whitespace(box.children[index], next_skip_stack)
        if result == 'continue':
            index += 1
            if index >= len(box.children):
                return 'continue'
            result = skip_first_whitespace(box.children[index], None)
        return index, result

    assert skip_stack is None, 'unexpected skip inside %s' % box
    return None


def remove_last_whitespace(document, box):
    """Remove in place space characters at the end of a line.

    This also reduces the width of the inline parents of the modified text.

    """
    ancestors = []
    while isinstance(box, (boxes.LineBox, boxes.InlineBox)):
        ancestors.append(box)
        if not box.children:
            return
        box = box.children[-1]
    if not (isinstance(box, boxes.TextBox) and
            box.style.white_space in ('normal', 'nowrap', 'pre-line')):
        return
    new_text = box.text.rstrip(' ')
    if new_text:
        if len(new_text) == len(box.text):
            return
        new_box, resume, _ = split_text_box(document, box, box.width * 2, 0)
        assert new_box is not None
        assert resume is None
        space_width = box.width - new_box.width
        box.width = new_box.width
        box.show_line = new_box.show_line
    else:
        space_width = box.width
        box.width = 0
        box.show_line = lambda x: x  # No-op
    box.text = new_text

    for ancestor in ancestors:
        ancestor.width -= space_width

    # TODO: All tabs (U+0009) are rendered as a horizontal shift that
    # lines up the start edge of the next glyph with the next tab stop.
    # Tab stops occur at points that are multiples of 8 times the width
    # of a space (U+0020) rendered in the block's font from the block's
    # starting content edge.

    # TODO: If spaces (U+0020) or tabs (U+0009) at the end of a line have
    # 'white-space' set to 'pre-wrap', UAs may visually collapse them.


def replaced_box_width(box, device_size):
    """
    Compute and set the used width for replaced boxes (inline- or block-level)
    """
    # http://www.w3.org/TR/CSS21/visudet.html#inline-replaced-width
    _surface, intrinsic_width, _intrinsic_height = box.replacement
    # TODO: update this when we have replaced elements that do not
    # always have an intrinsic width. (See commented code below.)
    assert intrinsic_width is not None

    if box.width == 'auto':
        box.width = intrinsic_width

    # Untested code for when we do not always have an intrinsic width.
#    intrinsic_ratio = intrinsic_width / intrinsic_height
#    if box.height == 'auto' and box.width == 'auto':
#        if intrinsic_width is not None:
#            box.width = intrinsic_width
#        elif intrinsic_height is not None and intrinsic_ratio is not None:
#            box.width = intrinsic_ratio * intrinsic_height
#        elif box.height != 'auto' and intrinsic_ratio is not None:
#            box.width = intrinsic_ratio * box.height
#        elif intrinsic_ratio is not None:
#            pass
#            # TODO: Intrinsic ratio only: undefined in CSS 2.1.
#            # " It is suggested that, if the containing block's width does not
#            #   itself depend on the replaced element's width, then the used
#            #   value of 'width' is calculated from the constraint equation
#            #   used for block-level, non-replaced elements in normal flow. "

#    # Still no value
#    if box.width == 'auto':
#        if intrinsic_width is not None:
#            box.width = intrinsic_width
#        else:
#            # Then the used value of 'width' becomes 300px. If 300px is too
#            # wide to fit the device, UAs should use the width of the largest
#            # rectangle that has a 2:1 ratio and fits the device instead.
#            device_width, _device_height = device_size
#            box.width = min(300, device_width)


def replaced_box_height(box, device_size):
    """
    Compute and set the used height for replaced boxes (inline- or block-level)
    """
    # http://www.w3.org/TR/CSS21/visudet.html#inline-replaced-height
    _surface, intrinsic_width, intrinsic_height = box.replacement
    # TODO: update this when we have replaced elements that do not
    # always have intrinsic dimensions. (See commented code below.)
    assert intrinsic_width is not None
    assert intrinsic_height is not None
    if intrinsic_height == 0:
        # Results in box.height == 0 if used, whatever the used width
        # or intrinsic width.
        intrinsic_ratio = float('inf')
    else:
        intrinsic_ratio = intrinsic_width / intrinsic_height

    # Test 'auto' on the computed width, not the used width
    if box.style.height == 'auto' and box.style.width == 'auto':
        box.height = intrinsic_height
    elif box.style.height == 'auto':
        box.height = box.width / intrinsic_ratio

    # Untested code for when we do not always have intrinsic dimensions.
#    if box.style.height == 'auto' and box.style.width == 'auto':
#        if intrinsic_height is not None:
#            box.height = intrinsic_height
#    elif intrinsic_ratio is not None and box.style.height == 'auto':
#        box.height = box.width / intrinsic_ratio
#    elif box.style.height == 'auto' and intrinsic_height is not None:
#        box.height = intrinsic_height
#    elif box.style.height == 'auto':
#        device_width, _device_height = device_size
#        box.height = min(150, device_width / 2)


def handle_min_max_width(function):
    """Decorate a function that sets the used width of a box to handle
    {min,max}-width.
    """
    @functools.wraps(function)
    def wrapper(box, *args):
        computed_margins = box.margin_left, box.margin_right
        function(box, *args)
        if box.width > box.max_width:
            box.width = box.max_width
            box.margin_left, box.margin_right = computed_margins
            function(box, *args)
        if box.width < box.min_width:
            box.width = box.min_width
            box.margin_left, box.margin_right = computed_margins
            function(box, *args)
    return wrapper


def handle_min_max_height(function):
    """Decorate a function that sets the used height of a box to handle
    {min,max}-height.
    """
    @functools.wraps(function)
    def wrapper(box, *args):
        computed_margins = box.margin_top, box.margin_bottom
        function(box, *args)
        if box.height > box.max_height:
            box.height = box.max_height
            box.margin_top, box.margin_bottom = computed_margins
            function(box, *args)
        if box.height < box.min_height:
            box.height = box.min_height
            box.margin_top, box.margin_bottom = computed_margins
            function(box, *args)
    return wrapper


min_max_replaced_width = handle_min_max_width(replaced_box_width)
min_max_replaced_height = handle_min_max_height(replaced_box_height)


def inline_replaced_box_layout(box, device_size):
    """Lay out an inline :class:`boxes.ReplacedBox` ``box``."""
    for side in ['top', 'right', 'bottom', 'left']:
        if getattr(box, 'margin_' + side) == 'auto':
            setattr(box, 'margin_' + side, 0)
    inline_replaced_box_width_height(box, device_size)

def inline_replaced_box_width_height(box, device_size):
    if box.style.width == 'auto' and box.style.height == 'auto':
        replaced_box_width(box, device_size)
        replaced_box_height(box, device_size)
        min_max_auto_replaced(box)
    else:
        min_max_replaced_width(box, device_size)
        min_max_replaced_height(box, device_size)


def min_max_auto_replaced(box):
    """Resolve {min,max}-{width,height} constraints on replaced elements
    that have 'auto' width and heights.
    """
    width = box.width
    height = box.height
    min_width = box.min_width
    min_height = box.min_height
    max_width = max(min_width, box.max_width)
    max_height = max(min_height, box.max_height)

    # (violation_width, violation_height)
    violations = (
        'min' if width < min_width else 'max' if width > max_width else '',
        'min' if height < min_height else 'max' if height > max_height else '')

    # Work around divisions by zero. These are pathological cases anyway.
    if width == 0:
        width = 1e-6
    if height == 0:
        height = 1e-6

    # ('', ''): nothing to do
    if violations == ('max', ''):
        box.width = max_width
        box.height = max(max_width * height / width, min_height)
    elif violations == ('min', ''):
        box.width = min_width
        box.height = min(min_width * height / width, max_height)
    elif violations == ('', 'max'):
        box.width = max(max_height * width / height, min_width)
        box.height = max_height
    elif violations == ('', 'min'):
        box.width = min(min_height * width / height, max_width)
        box.height = min_height
    elif violations == ('max', 'max'):
        if max_width / width <= max_height / height:
            box.width = max_width
            box.height = max(min_height, max_width * height / width)
        else:
            box.width = max(min_width, max_height * width / height)
            box.height = max_height
    elif violations == ('min', 'min'):
        if min_width / width <= min_height / height:
            box.width = min(max_width, min_height * width / height)
            box.height = min_height
        else:
            box.width = min_width
            box.height = min(max_height, min_width * height / width)
    elif violations == ('min', 'max'):
        box.width = min_width
        box.height = max_height
    elif violations == ('max', 'min'):
        box.width = max_width
        box.height = min_height


def atomic_box(document, box, position_x, skip_stack, containing_block,
               device_size, absolute_boxes):
    """Compute the width and the height of the atomic ``box``."""
    if isinstance(box, boxes.ReplacedBox):
        if getattr(box, 'is_list_marker', False):
            image_marker_layout(box)
        else:
            inline_replaced_box_layout(box, device_size)
        box.baseline = box.margin_height()
    elif isinstance(box, boxes.InlineBlockBox):
        if box.is_table_wrapper:
            table_wrapper_width(
                document, box,
                (containing_block.width, containing_block.height),
                absolute_boxes)
        box = inline_block_box_layout(
            document, box, position_x, skip_stack, containing_block,
            device_size, absolute_boxes)
    else:  # pragma: no cover
        raise TypeError('Layout for %s not handled yet' % type(box).__name__)
    return box


def inline_block_box_layout(document, box, position_x, skip_stack,
                            containing_block, device_size, absolute_boxes):
    # Avoid a circular import
    from .blocks import block_container_layout

    resolve_percentages(box, containing_block)

    # http://www.w3.org/TR/CSS21/visudet.html#inlineblock-width
    if box.margin_left == 'auto':
        box.margin_left = 0
    if box.margin_right == 'auto':
        box.margin_right = 0

    inline_block_width(box, document, containing_block)

    box.position_x = position_x
    box.position_y = 0
    box, _, _, _, _ = block_container_layout(
        document, box, max_position_y=float('inf'), skip_stack=skip_stack,
        device_size=device_size, page_is_empty=True,
        absolute_boxes=absolute_boxes)
    box.baseline = inline_block_baseline(box)
    return box


def inline_block_baseline(box):
    """
    Return the y position of the baseline for an inline block
    from the top of its margin box.

    http://www.w3.org/TR/CSS21/visudet.html#propdef-vertical-align

    """
    if box.style.overflow == 'visible':
        result = find_in_flow_baseline(box, last=True)
        if result:
            return result
    return box.position_y + box.margin_height()


@handle_min_max_width
def inline_block_width(box, document, containing_block):
    if box.width == 'auto':
        box.width = shrink_to_fit(document, box, containing_block.width)


def split_inline_level(document, box, position_x, max_x, skip_stack,
                       containing_block, device_size, absolute_boxes,
                       line_placeholders):
    """Fit as much content as possible from an inline-level box in a width.

    Return ``(new_box, resume_at)``. ``resume_at`` is ``None`` if all of the
    content fits. Otherwise it can be passed as a ``skip_stack`` parameter
    to resume where we left off.

    ``new_box`` is non-empty (unless the box is empty) and as big as possible
    while being narrower than ``available_width``, if possible (may overflow
    is no split is possible.)

    """
    resolve_percentages(box, containing_block)
    if isinstance(box, boxes.TextBox):
        box.position_x = position_x
        if skip_stack is None:
            skip = 0
        else:
            skip, skip_stack = skip_stack
            skip = skip or 0
            assert skip_stack is None

        new_box, skip, preserved_line_break = split_text_box(
            document, box, max_x - position_x, skip)

        if skip is None:
            resume_at = None
        else:
            resume_at = (skip, None)
    elif isinstance(box, boxes.InlineBox):
        if box.margin_left == 'auto':
            box.margin_left = 0
        if box.margin_right == 'auto':
            box.margin_right = 0
        new_box, resume_at, preserved_line_break = split_inline_box(
            document, box, position_x, max_x, skip_stack, containing_block,
            device_size, absolute_boxes, line_placeholders)
    elif isinstance(box, boxes.AtomicInlineLevelBox):
        new_box = atomic_box(
            document, box, position_x, skip_stack, containing_block,
            device_size, absolute_boxes)
        new_box.position_x = position_x
        resume_at = None
        preserved_line_break = False
    #else: unexpected box type here
    return new_box, resume_at, preserved_line_break


def split_inline_box(document, box, position_x, max_x, skip_stack,
                     containing_block, device_size, absolute_boxes,
                     line_placeholders):
    """Same behavior as split_inline_level."""
    initial_position_x = position_x
    assert isinstance(box, (boxes.LineBox, boxes.InlineBox))
    left_spacing = (box.padding_left + box.margin_left +
                    box.border_left_width)
    right_spacing = (box.padding_right + box.margin_right +
                     box.border_right_width)
    position_x += left_spacing
    content_box_left = position_x

    children = []
    preserved_line_break = False

    is_start = skip_stack is None
    if is_start:
        skip = 0
    else:
        skip, skip_stack = skip_stack

    if box.style.position == 'relative':
        absolute_boxes = []

    for index, child in box.enumerate_skip(skip):
        child.position_y = box.position_y
        if not child.is_in_normal_flow():
            if child.style.position in ('absolute', 'fixed'):
                child.position_x = position_x
                placeholder = AbsolutePlaceholder(child)
                line_placeholders.append(placeholder)
                if child.style.position == 'absolute':
                    absolute_boxes.append(placeholder)
                    children.append(placeholder)
                else:
                    document.fixed_boxes.append(placeholder)
            else:
                # TODO: Floats
                children.append(child)
            continue

        new_child, resume_at, preserved = split_inline_level(
            document, child, position_x, max_x, skip_stack,
            containing_block, device_size, absolute_boxes, line_placeholders)
        skip_stack = None
        if preserved:
            preserved_line_break = True

        # TODO: this is non-optimal when last_child is True and
        #   width <= remaining_width < width + right_spacing
        # with
        #   width = part1.margin_width()

        # TODO: on the last child, take care of right_spacing

        if new_child is None:
            # may be None where we would have an empty TextBox
            assert isinstance(child, boxes.TextBox)
        else:
            margin_width = new_child.margin_width()
            new_position_x = position_x + margin_width

            if (new_position_x > max_x and children):
                # too wide, and the inline is non-empty:
                # put child entirely on the next line.
                resume_at = (index, None)
                break
            else:
                position_x = new_position_x
                children.append(new_child)

        if resume_at is not None:
            resume_at = (index, resume_at)
            break
    else:
        resume_at = None

    new_box = box.copy_with_children(
        children, is_start=is_start, is_end=resume_at is None)
    if isinstance(box, boxes.LineBox):
        # Line boxes already have a position_x which may not be the same
        # as content_box_left when text-indent is non-zero.
        # This is important for justified text.
        new_box.width = position_x - new_box.position_x
    else:
        new_box.position_x = initial_position_x
        new_box.width = position_x - content_box_left

    # Create a "strut":
    # http://www.w3.org/TR/CSS21/visudet.html#strut
    # TODO: cache these results for a given set of styles?
    fragment = TextFragment(
        '', box.style, cairo.Context(document.surface))
    _, _, _, height, baseline, _ = fragment.split_first_line()
    leading = used_line_height(box.style) - height
    half_leading = leading / 2.
    # Set margins to the half leading but also compensate for borders and
    # paddings. We want margin_height() == line_height
    new_box.margin_top = (half_leading - new_box.border_top_width -
                          new_box.padding_bottom)
    new_box.margin_bottom = (half_leading - new_box.border_bottom_width -
                             new_box.padding_bottom)
    # form the top of the content box
    new_box.baseline = baseline
    # form the top of the margin box
    new_box.baseline += half_leading
    new_box.height = height

    if new_box.style.position == 'relative':
        for absolute_box in absolute_boxes:
            absolute_layout(document, absolute_box, new_box)
    return new_box, resume_at, preserved_line_break


def split_text_box(document, box, available_width, skip):
    """Keep as much text as possible from a TextBox in a limitied width.
    Try not to overflow but always have some text in ``new_box``

    Return ``(new_box, skip)``. ``skip`` is the number of UTF-8 bytes
    to skip form the start of the TextBox for the next line, or ``None``
    if all of the text fits.

    Also break an preserved whitespace.

    """
    assert isinstance(box, boxes.TextBox)
    font_size = box.style.font_size
    text = box.text[skip:]
    if font_size == 0 or not text:
        return None, None, False
    fragment = TextFragment(text, box.style,
        cairo.Context(document.surface), available_width)

    # XXX ``resume_at`` is an index in UTF-8 bytes, not unicode codepoints.
    show_line, length, width, height, baseline, resume_at = \
        fragment.split_first_line()

    # Convert ``length`` and ``resume_at`` from UTF-8 indexes in text
    # to Unicode indexes.
    # No need to encode what’s after resume_at (if set) or length (if
    # resume_at is not set). One code point is one or more byte, so
    # UTF-8 indexes are always bigger or equal to Unicode indexes.
    partial_text = text[:resume_at or length]
    utf8_text = partial_text.encode('utf8')
    new_text = utf8_text[:length].decode('utf8')
    new_length = len(new_text)
    if resume_at is not None:
        between = utf8_text[length:resume_at].decode('utf8')
        resume_at = new_length + len(between)
    length = new_length

    if length > 0:
        box = box.copy_with_text(new_text)
        box.width = width
        box.show_line = show_line
        # "The height of the content area should be based on the font,
        #  but this specification does not specify how."
        # http://www.w3.org/TR/CSS21/visudet.html#inline-non-replaced
        # We trust Pango and use the height of the LayoutLine.
        # It is based on font_size (slightly larger), but I’m not sure how.
        # TODO: investigate this
        box.height = height
        # "only the 'line-height' is used when calculating the height
        #  of the line box."
        # Set margins so that margin_height() == line_height
        leading = used_line_height(box.style) - height
        half_leading = leading / 2.
        box.margin_top = half_leading
        box.margin_bottom = half_leading
        # form the top of the content box
        box.baseline = baseline
        # form the top of the margin box
        box.baseline += box.margin_top + box.border_top_width + box.padding_top
    else:
        box = None

    if resume_at is None:
        preserved_line_break = False
    else:
        preserved_line_break = (length != resume_at)
        if preserved_line_break:
            # See http://unicode.org/reports/tr14/
            # TODO: are there others? Find Pango docs on this
            assert between in ('\n', '\u2029'), (
                'Got %r between two lines. '
                'Expected nothing or a preserved line break' % (between,))
        resume_at += skip

    return box, resume_at, preserved_line_break


def inline_box_verticality(box, baseline_y):
    """Handle ``vertical-align`` within an :class:`InlineBox`.

    Place all boxes vertically assuming that the baseline of ``box``
    is at `y = baseline_y`.

    Return ``(max_y, min_y)``, the maximum and minimum vertical position
    of margin boxes.

    """
    max_y = None
    min_y = None
    for child in box.children:
        if not child.is_in_normal_flow():
            continue
        vertical_align = child.style.vertical_align
        if vertical_align == 'baseline':
            child_baseline_y = baseline_y
        elif vertical_align == 'middle':
            # TODO: find ex from font metrics
            one_ex = box.style.font_size * 0.5
            top = baseline_y - (one_ex + child.margin_height()) / 2.
            child_baseline_y = top + child.baseline
        # TODO: actually implement vertical-align: top and bottom
        elif vertical_align in ('text-top', 'top'):
            # align top with the top of the parent’s content area
            top = (baseline_y - box.baseline + box.margin_top +
                   box.border_top_width + box.padding_top)
            child_baseline_y = top + child.baseline
        elif vertical_align in ('text-bottom', 'bottom'):
            # align bottom with the bottom of the parent’s content area
            bottom = (baseline_y - box.baseline + box.margin_top +
                      box.border_top_width + box.padding_top + box.height)
            child_baseline_y = bottom - child.margin_height() + child.baseline
        else:
            # Numeric value: The child’s baseline is `vertical_align` above
            # (lower y) the parent’s baseline.
            child_baseline_y = baseline_y - vertical_align
        # the child’s `top` is `child.baseline` above (lower y) its baseline.
        top = child_baseline_y - child.baseline
        if isinstance(child, boxes.InlineBlockBox):
            # This also includes table wrappers for inline tables.
            child.translate(dy=top - child.position_y)
        else:
            child.position_y = top
            # grand-children for inline boxes are handled below
        bottom = top + child.margin_height()
        if min_y is None or top < min_y:
            min_y = top
        if max_y is None or bottom > max_y:
            max_y = bottom
        if isinstance(child, boxes.InlineBox):
            children_max_y, children_min_y = inline_box_verticality(
                child, child_baseline_y)
            if children_max_y is None:
                if (
                    child.margin_width() == 0
                    # Guard against the case where a negative margin
                    # compensates something else.
                    and child.margin_left == 0
                    and child.margin_right == 0
                ):
                    # No content, ignore this box’s line-height.
                    # See http://www.w3.org/TR/CSS21/visuren.html#phantom-line-box
                    child.position_y = child_baseline_y
                    child.height = 0
                    continue
            else:
                assert children_min_y is not None
                if children_min_y < min_y:
                    min_y = children_min_y
                if children_max_y > max_y:
                    max_y = children_max_y
    return max_y, min_y


def text_align(document, line, containing_block, last):
    """Return how much the line should be moved horizontally according to
    the `text-align` property.

    """
    align = line.style.text_align
    if align in ('-weasy-start', '-weasy-end'):
        if (align == '-weasy-start') ^ (line.style.direction == 'rtl'):
            align = 'left'
        else:
            align = 'right'
    if align == 'justify' and last:
        align = 'right' if line.style.direction == 'rtl' else 'left'
    if align == 'left':
        return 0
    offset = containing_block.width - line.width
    if align == 'justify':
        justify_line(document, line, offset)
        return 0
    if align == 'center':
        offset /= 2.
    else:
        assert align == 'right'
    return offset


def justify_line(document, line, extra_width):
    nb_spaces = count_spaces(line)
    if nb_spaces == 0:
        # TODO: what should we do with single-word lines?
        return
    add_word_spacing(document, line, extra_width / nb_spaces, 0)


def count_spaces(box):
    if isinstance(box, boxes.TextBox):
        # TODO: remove trailing spaces correctly
        return box.text.count(' ')
    elif isinstance(box, (boxes.LineBox, boxes.InlineBox)):
        return sum(count_spaces(child) for child in box.children)
    else:
        return 0


def add_word_spacing(document, box, extra_word_spacing, x_advance):
    if isinstance(box, boxes.TextBox):
        box.position_x += x_advance
        box.style.word_spacing += extra_word_spacing
        nb_spaces = count_spaces(box)
        if nb_spaces > 0:
            new_box, resume_at, _ = split_text_box(
                document, box, 1e10, 0)
            assert new_box is not None
            assert resume_at is None
            # XXX new_box.width - box.width is always 0???
            #x_advance +=  new_box.width - box.width
            x_advance += extra_word_spacing * nb_spaces
            box.width = new_box.width
            box.show_line = new_box.show_line
    elif isinstance(box, (boxes.LineBox, boxes.InlineBox)):
        box.position_x += x_advance
        previous_x_advance = x_advance
        for child in box.children:
            x_advance = add_word_spacing(
                document, child, extra_word_spacing, x_advance)
        box.width += x_advance - previous_x_advance
    else:
        # Atomic inline-level box
        box.translate(x_advance, 0)
    return x_advance
