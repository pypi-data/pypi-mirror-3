<%inherit file="/base.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/index.css'))}
</%def>

<%def name="context_menu_items()"></%def>

<div class="object-index">
  <div class="wrapper">

    <ul id="context-menu">
      ${self.context_menu_items()}
    </ul>

    <div class="left">
      ${search.render()|n}
    </div>
  </div>

  ${grid|n}

</div>
