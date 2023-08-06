from django import template
from django_extrawidgets.validation import JavascriptValidation


register = template.Library()


class JavascriptValidationNode(template.Node):
    def __init__(self, form, *fields):
        self.form = form
        self.fields = fields

    def render(self, context):
        form = self.form.resolve(context)
        js = JavascriptValidation(form)

        html = []
        html.append(u'(function ($) {')
        html.append(u'var interpolate = $.rays.interpolate')
        html.append(js)
        html.append(u'})(jQuery);')
        return u'\n'.join([unicode(line) for line in html])

    @classmethod
    def parse(cls, parser, tokens):
        bits = tokens.split_contents()
        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                u'%s tag expects at least one argument.' % bits[0])
        form_field = template.Variable(bits[1])
        return cls(form_field)


class ScriptValidationNode(JavascriptValidationNode):
    def render(self, context):
        js = super(JavascriptValidationNode, self).render(context)
        return '<script type="text/javascript">%s//</script>' % js


register.tag('validatejs', JavascriptValidationNode.parse)
register.tag('validate', ScriptValidationNode.parse)
