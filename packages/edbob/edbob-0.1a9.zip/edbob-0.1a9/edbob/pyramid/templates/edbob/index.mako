<%inherit file="/base.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/index.css'))}
</%def>

<%def name="context_menu_items()"></%def>
<%def name="tools()"></%def>

<div class="object-index">

  <table class="header">
    <tr>
      % if search:
          <td rowspan="2" class="filters">
            ${search.render()}
          </td>
      % else:
          <td rowspan="2">&nbsp;</td>
      % endif
      <td class="context-menu">
        <ul>
          ${self.context_menu_items()}
        </ul>
      </td>
    </tr>
    <tr>
      <td class="tools">
        ${self.tools()}
      </td>
    </tr>
  </table>

  ${grid}

</div>
