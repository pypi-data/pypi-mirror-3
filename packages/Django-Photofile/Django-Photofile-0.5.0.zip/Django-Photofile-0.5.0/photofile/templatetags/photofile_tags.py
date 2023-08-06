#coding=utf-8
from django.template import resolve_variable
from django import template
from photofile import get_filename, generate_thumb

register = template.Library()

@register.tag(name="generate_thumbnail")
def generate_thumbnail(parser, token):
    use_uid = None
    try:
        tokens = token.split_contents()
        if len(tokens) == 3:
            tagname, photo, resolution = tokens
            crop = False
        elif len(tokens) == 4:
            tagname, photo, resolution, option = tokens
            crop = option == "crop"
        elif len(tokens) == 5:
            tagname, photo, resolution, option, use_uid = tokens
            crop = option == "crop"
        else:
            raise Exception("Invalid param count for templatetag generate_thumbnail. Got '%s' [%s items]" % ((tokens, len(tokens))))
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two or three arguments." % tagname
    except Exception, e:
        raise Exception("Error executing templatetag generate_thumbnail. Exception raised: %s" % e)
    return FormatImageNode(photo, resolution, crop, use_uid)


class FormatImageNode(template.Node):

    def __init__(self, photo, resolution, do_crop=False, use_uid=False):
        self.resolution = resolution
        self.photo = template.Variable(photo)
        self.do_crop = do_crop
        self.use_uid = use_uid

    def render(self, context):
        try:

            if self.resolution.find('max') == -1 and 'x' not in self.resolution:
                return 'not correct resolution format'

            p = self.photo.resolve(context)
            complete_filename = p.complete_filename

            unique_identifier = (self.use_uid and hasattr(p, 'unique_identifier')) and p.unique_identifier or None

            if self.resolution.find('max') != -1:
                request = context['request']
                height, width = request.session['screen_height'], request.session['screen_width']

                if '-' in self.resolution:
                    modifier = self.resolution.split('-')[-1]
                    if '%' in modifier:
                        actual_modifier = float('0.%s' % modifier.replace('%', ''))
                        height = int(height) * actual_modifier
                        width = int(width) * actual_modifier
                    else:
                        height = int(height) - int(modifier)
                        width = int(width) - int(modifier)
            else:
                width, height = map(int, self.resolution.split('x'))

            return generate_thumb(complete_filename, width, height, self.do_crop, unique_identifier)
        except template.VariableDoesNotExist, e:
            return 'Unable to produce url for image: %s' % e