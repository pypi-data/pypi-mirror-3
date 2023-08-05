from zope import component, schema

from Products.Five.browser import BrowserView

from Products.Archetypes.utils import DisplayList
from Products.Archetypes.Widget import TypesWidget, StringWidget, LinesWidget
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget

from Products.CMFPlone.utils import safe_unicode

from raptus.autocompletewidget.interfaces import ISearchableVocabulary

class AutocompleteSearch(BrowserView):
    
    def __call__(self):
        
        field = self.request.get('f', None)
        query = safe_unicode(self.request.get('q', ''))
        limit = self.request.get('limit', None)
        if not query or not field:
            return ''
        
        field = self.context.Schema().getField(field)
        if not field:
            return ''
        
        vocabulary = field.vocabulary
        if not isinstance(vocabulary, DisplayList) and not vocabulary:
            factory_name = getattr(field, 'vocabulary_factory', None)
            if factory_name is not None:
                factory = component.getUtility(schema.interfaces.IVocabularyFactory, name=factory_name)
                vocabulary = factory(self.context)
        if ISearchableVocabulary.providedBy(vocabulary):
            results = vocabulary.search(query, self.context)
        else:
            query = query.lower()
            vocab = field.Vocabulary(self.context).items()
            results = [(value, title) for value, title in vocab if query in value.lower() or query in title.lower()]
        
        return '\n'.join(["%s|%s" % (value, title) for value, title in results])
    
class AutocompletePopulate(AutocompleteSearch):
    
    def __call__(self):
        results = super(AutocompletePopulate, self).__call__()
        results = results.split('\n')
        query = self.request.get('q', '')
        for r in results:
            if r.startswith(u'%s|' % safe_unicode(query)):
                return r
        
class AutocompleteBaseWidget(TypesWidget):
    _properties = {
        'blurrable' : False,
        'minChars' : 2,
        'maxResults' : 10,
        'mustMatch' : False,
        'matchContains' : True,
        'formatItem' : 'function(row, idx, count, value) { return row[1]; }',
        'formatResult': 'function(row, idx, count) { return ""; }',
        }
    
    # JavaScript template
    
    js_template = """\
    (function($) {
        $().ready(function() {
            $('#archetypes-fieldname-%(id)s #%(id)s').each(function() {
                $('#archetypes-fieldname-%(id)s').append('<input name="%(id)s-input" type="text" id="%(id)s-input" />');
                %(js_populate)s
                $(this).remove();
                $('#archetypes-fieldname-%(id)s #%(id)s-input').autocomplete('%(url)s/@@autocompletewidget-search?f=%(id)s', {
                    autoFill: false,
                    minChars: %(minChars)d,
                    max: %(maxResults)d,
                    mustMatch: %(mustMatch)s,
                    matchContains: %(matchContains)s,
                    formatItem: %(formatItem)s,
                    formatResult: %(formatResult)s
                }).result(%(js_callback)s);
            })
        });
    })(jQuery);
    """
    
    def js(self, instance, fieldName):
        
        form_url = instance.absolute_url()

        js_callback = self.js_callback_template % dict(id=fieldName)
        js_populate = self.js_populate_template % dict(id=fieldName, url=form_url)
        
        return self.js_template % dict(id=fieldName,
                                       url=form_url,
                                       minChars=self.minChars,
                                       maxResults=self.maxResults,
                                       mustMatch=str(self.mustMatch).lower(),
                                       matchContains=str(self.matchContains).lower(),
                                       formatItem=self.formatItem,
                                       formatResult=self.formatResult,
                                       js_callback=js_callback,
                                       js_populate=js_populate,)

class AutocompleteSelectionWidget(AutocompleteBaseWidget):
    _properties = StringWidget._properties.copy()
    _properties.update(AutocompleteBaseWidget._properties)
    _properties.update({
        'macro' : "autocomplete",
        })
    
    # JavaScript template
    
    # the funny <" + "input bit is to prevent breakage in testbrowser tests
    # when it parses the js as a real input, but with a bogus value
    js_callback_template = """\
    function(event, data, formatted) {
        var field = $('#archetypes-fieldname-%(id)s input[type="radio"][value="' + data[0] + '"]');
        if(field.length == 0)
            $('#archetypes-fieldname-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='radio' name='%(id)s' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
        else
            field.each(function() { this.checked = true });
        if(data[0])
            $('#archetypes-fieldname-%(id)s #%(id)s-input').val('');
    }
    """
    
    js_populate_template = """\
    var value = $(this).val();
    if(value)
        $.get('%(url)s/@@autocompletewidget-populate', {'f': '%(id)s', 'q': value}, function(data) {
            if(data) {
                data = data.split('|');
                $('#archetypes-fieldname-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='radio' name='%(id)s' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
            }
        });
    """
    
class AutocompleteMultiSelectionWidget(AutocompleteBaseWidget):
    _properties = LinesWidget._properties.copy()
    _properties.update(AutocompleteBaseWidget._properties)
    _properties.update({
        'macro' : "autocompletemulti",
    })
    
    # JavaScript template
    
    # the funny <" + "input bit is to prevent breakage in testbrowser tests
    # when it parses the js as a real input, but with a bogus value
    js_callback_template = """\
    function(event, data, formatted) {
        var field = $('#archetypes-fieldname-%(id)s input[type="checkbox"][value="' + data[0] + '"]');
        if(field.length == 0)
            $('#archetypes-fieldname-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='checkbox' name='%(id)s:list' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
        else
            field.each(function() { this.checked = true });
        if(data[0])
            $('#archetypes-fieldname-%(id)s #%(id)s-input').val('');
    }
    """
    
    js_populate_template = """\
    value = $(this).text().split("\\n");
    if(value)
        for(var i=0; i<value.length; i++)
            $.get('%(url)s/@@autocompletewidget-populate', {'f': '%(id)s', 'q': value[i]}, function(data) {
                if(data) {
                    data = data.split('|');
                    $('#archetypes-fieldname-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='checkbox' name='%(id)s:list' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
                }
            });
    """

registerWidget(AutocompleteSelectionWidget,
               title='Autocomplete selection',
               description=(''),
               used_for=('Products.Archetypes.Field.StringField',)
               )

registerWidget(AutocompleteMultiSelectionWidget,
               title='Autocomplete multiselection',
               description=(''),
               used_for=('Products.Archetypes.Field.LinesField',)
               )

registerPropertyType('autoFill', 'boolean', AutocompleteSelectionWidget)
registerPropertyType('minChars', 'integer', AutocompleteSelectionWidget)
registerPropertyType('maxResults', 'integer', AutocompleteSelectionWidget)
registerPropertyType('mustMatch', 'boolean', AutocompleteSelectionWidget)
registerPropertyType('matchContains', 'boolean', AutocompleteSelectionWidget)
registerPropertyType('formatItem', 'string', AutocompleteSelectionWidget)
registerPropertyType('formatResult', 'string', AutocompleteSelectionWidget)
        