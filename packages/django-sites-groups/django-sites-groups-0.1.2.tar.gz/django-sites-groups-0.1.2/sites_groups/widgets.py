from django.forms.widgets import SelectMultiple
from django.template.loader import get_template_from_string
from django.template import Context
from django.utils.translation import ugettext as _

from sites_groups.models import SitesGroup


TEMPLATE = '''
{% if groups %}
{% load i18n %}
<script type="text/javascript">
function on{{ name }}SitesGroupClick(sender){
    var select = document.getElementById('id_{{ name }}');    
    var ids = sender.getAttribute('site_ids').split(',');
    for (var i=0; i < select.options.length; i++)
    {
        var value = select[i].value;
        if (ids.indexOf(value) != -1)
            select[i].selected = true;
        else
            select[i].selected = false;
    }
}
</script>
{% trans "Click an item to select" %}
<ul style="margin: 0 0 0 8px; padding: 0;">
    {% for group in groups %}
        <li>
            <a href="#" onclick="on{{ name }}SitesGroupClick(this);return false;" site_ids="{{ group.site_ids|join:"," }}">
                {{ group.title }}
            </a>
        </li>
    {% endfor %}
</ul>
{% endif %}'''


class SitesGroupsWidget(SelectMultiple):

    def render(self, name, value, attrs=None, choices=()):                
        template = get_template_from_string(TEMPLATE)
        di = dict(name=name, groups=SitesGroup.objects.all())
        html = template.render(Context(di))
        select = super(SitesGroupsWidget, self).render(name, value, attrs=attrs, choices=choices)
        return '<table style="border: 0;"><tr><td>' + select + '</td><td>' + html + '</td></tr></table>'
