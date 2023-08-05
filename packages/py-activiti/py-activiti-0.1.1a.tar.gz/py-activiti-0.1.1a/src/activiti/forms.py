#    Coding: utf-8

#    py-activiti - Python Wrapper For Activiti BPMN2.0 API
#    Copyright (C) 2011  xtensive.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

#FIXME: is this module really useful ???

from django.template import loader
from django.template.context import RequestContext

INPUT_TEXT = '<input type="text" value="%{value}" name="%{id} class="v-textfield" %{disabled} %{required}/>'
INPUT_TEXT_HIDDEN = '<input type="hidden" value="%{value}" name="%{id} class="v-hidden-textfield" />'
INPUT_CHECKBOX = '<input type="checkbox" name="%{id}" value="%{value}" %{disabled} />'
INPUT_TEXTAREA = '<textarea name="%{id}" %{disabled} %{required}>%{value}</textarea>'
INPUT_RADIO = '<input type="radio" name="${id}" value="%{value}" %{disabled} />'
INPUT_DATE = '<input type="date" value="%{value}" name="%{id} %{disabled} %{required}/>'

SELECT = '<select >%s</select>'
OPTION = '<option value="%{id}" %{selected}>%{name}</option>'

INPUT_TYPE = '<input type="text" name="%{id}_type" value="%{type}" %{disabled} />'




def form_generator(form_properties, request=None):
    '''
    '''
    _widgets = []
    for props in form_properties:
        _wgt = {}
        
        
        if not props['writable']:
            _wgt['disabled'] = "disabled"
        else:
            _wgt['disabled'] = ''
        
        label = props['name']
        required = props['required']
        var_type = props['type']
        id = props['id']
        
        if not props['readable']:
            _wgt['ui'] = INPUT_TEXT_HIDDEN
        else:
            if var_type == 'string':
                _ui =  INPUT_TEXT
            elif var_type == 'boolean':
                _wgt['ui'] = INPUT_CHECKBOX
            elif var_type == 'long':
                pass
            
    t = loader.get_template('form.html')
    if request:
        c = RequestContext(request, {'foo': 'bar'})
    else:
        c = {}
    return t.render(c)    
        
    