from django.template import Library, TemplateSyntaxError


from easy_thumbnails.templatetags.thumbnail import thumbnail
from easy_thumbnails import utils


VALID_OPTIONS = utils.valid_processor_options()



def cropped_thumbnail(parser, token):
    """
    Creates a thumbnail based on an ImageRatioField

    Basic tag Syntax::

        {% cropped_thumbnail instance "cropping_field_name" [options] %}

    *instance* must be any object with an attribute named "cropping_field_name". This
    attribute is expected to be either an ImageCropField or CropForeignKey. The
    thumbnail is generated from either of those.

    *options* are a space separated list of options which are used when
    processing the image to a thumbnail such as ``sharpen``, ``crop`` and
    ``quality=90``.

    The size can be passed in as an option in the form "widthxheight" or left out,
    in that case the size defined in the ImageRatioField will be used.

    The thumbnail tag can also place a ``ThumbnailFile`` object in the context,
    providing access to the properties of the thumbnail such as the height and
    width::

        {% cropped_thumbnail instance "image_field_name" [options] as [variable] %}

    When ``as [variable]`` is used, the tag does not return the absolute URL of
    the thumbnail.

    """

    args = token.split_contents()
    tag, instance, field_name = args[:3]
    args = args[3:]

    # The first argument is the source file.
    instance_var = parser.compile_filter(args[1])

    token.contents = 'thumbnail %s "%s" %s' % (
        thumbnail_var, size, ' '.join(args))

    return thumbnail(parser, token)
    # Check to see if we're setting to a context variable.
    if len(args) > 3 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None

    if len(args) < 3:
        raise TemplateSyntaxError("Invalid syntax. Expected "
            "'{%% %s instance field_name [option1 option2 ...] %%}' or "
            "'{%% %s instance field_name [option1 option2 ...] as variable %%}'" %
            (tag, tag))

    opts = {}


    # All further arguments are options.
    args_list = split_args(args[3:]).items()
    for arg, value in args_list:
        if arg in VALID_OPTIONS:
            if value and value is not True:
                value = parser.compile_filter(value)
            opts[arg] = value
        else:
            raise TemplateSyntaxError("'%s' tag received a bad argument: "
                                      "'%s'" % (tag, arg))
    return ThumbnailNode(source_var, opts=opts, context_name=context_name)


register = Library()
register.tag(cropped_thumbnail)
