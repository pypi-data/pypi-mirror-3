<%inherit file="/base.mako" />

<%def name="title()">${(fieldset.crud_title+' : '+fieldset.get_display_text() if fieldset.edit else 'New '+fieldset.crud_title) if crud else ''|n}</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">

    #context-menu {
        float: right;
    }

    div.fieldset {
        float: left;
    }

  </style>
</%def>

<%def name="context_menu_items()"></%def>

<div class="wrapper">

  <ul id="context-menu">
    ${self.context_menu_items()}
  </ul>

  ${fieldset.render()|n}

</div>
