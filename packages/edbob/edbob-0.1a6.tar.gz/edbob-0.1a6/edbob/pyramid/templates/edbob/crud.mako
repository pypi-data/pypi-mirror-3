<%inherit file="/base.mako" />

<div class="crud wrapper">

  <div class="right">
    ${self.menu()}
  </div>

  <div class="left">
    ${fieldset.render()|n}
  </div>

</div>
