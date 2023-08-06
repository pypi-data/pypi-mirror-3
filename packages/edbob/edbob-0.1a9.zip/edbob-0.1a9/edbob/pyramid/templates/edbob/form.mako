<%inherit file="/base.mako" />

<%def name="buttons()"></%def>

<div class="wrapper">

  <div class="right">
    ${self.menu()}
  </div>

  <div class="left">
    <% print 'type (2) is', type(form) %>
    ${form.render(buttons=self.buttons)|n}
  </div>

</div>
