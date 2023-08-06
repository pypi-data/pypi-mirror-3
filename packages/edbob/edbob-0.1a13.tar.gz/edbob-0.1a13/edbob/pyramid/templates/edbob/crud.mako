<%inherit file="/form.mako" />

<%def name="title()">${"New "+form.pretty_name if form.creating else form.pretty_name+' : '+str(form.fieldset.model)}</%def>

${parent.body()}
