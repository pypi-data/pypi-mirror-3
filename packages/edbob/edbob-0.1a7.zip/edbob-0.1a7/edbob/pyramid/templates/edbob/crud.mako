<%inherit file="/base.mako" />

<%def name="title()">${(fieldset.crud_title+' : '+fieldset.get_display_text() if fieldset.edit else 'New '+fieldset.crud_title) if crud else ''}</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/crud.css'))}
</%def>

<%def name="context_menu_items()"></%def>

<div class="crud wrapper">

  <ul id="context-menu">
    ${self.context_menu_items()}
  </ul>

  <div class="left">
    ${fieldset.render()|n}
  </div>

</div>
