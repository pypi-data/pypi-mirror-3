
from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.simple_tag(takes_context=True)
def openonmobile_image_url(context, **kwargs):
    request = context['request']
    url = "%s?url=%s" % (reverse('openonmobile_qr'), request.path)
    if 'rotate' in kwargs:
        url = url + "&rotate=%s" % kwargs['rotate']
    return url


@register.simple_tag(takes_context=True)
def openonmobile_img(context, **kwargs):
    request = context['request']
    url = "%s?url=%s" % (reverse('openonmobile_qr'), request.path)
    if 'rotate' in kwargs:
        url = url + "&rotate=%s" % kwargs['rotate']
        del kwargs['rotate']
    attrs = {'src': url}
    attrs.update(kwargs)
    attrs = ['%s="%s"' % (k, v) for k, v in attrs.iteritems()]
    return '<img %s>' % " ".join(attrs)
