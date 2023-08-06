<%inherit file="/base.mako" />

<%def name="context_menu_items()"></%def>
<%def name="tools()"></%def>

<div class="grid-wrapper">

  <table class="grid-header">
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
  </table><!-- grid-header -->

  ${grid}

</div><!-- grid-wrapper -->
