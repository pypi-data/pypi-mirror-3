import floppyforms as forms
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _

class MarkdownTextarea(forms.Textarea):
    template_name = 'samklang_utils/markdown_textarea.html'

    class Media:
        js = ('js/wmd.js', 'js/showdown.js', 'js/flext.js')
        css = {
                'all': ('css/wmd.css',)
                }

    def get_context_data(self):
        self.attrs['class'] += " flext growme maxheight-500"
        return super(MarkdownTextarea, self).get_context_data()

class AutoupdateTextInput(forms.TextInput):
    template_name = 'samklang_utils/autoupdate_text_input.html'

class GroupSelect(forms.Select):

    #def __init__(self, attrs=None, choices=()):
    #    super(forms.Select, self).__init__(attrs)
    #    print self.choices
    #    self.choices.insert(0, ('0', '---'))
    #    print self.choices
    #    #self.choices = list(choices)

    def render(self, name, value, attrs=None, choices=()):
        #self.choices.insert((0, '---'))
        from itertools import chain
        self.choices = chain((('0', _('Nobody')),('', _('Public'))), self.choices)
        self.initial = '0'
        #print dir(self.choices)
        #print self.choices.queryset
        #print self.choices.choice
        #print self.choices.field
        return super(GroupSelect, self).render(name, value, attrs, ())

class GroupField(ModelChoiceField):
    widget = GroupSelect


