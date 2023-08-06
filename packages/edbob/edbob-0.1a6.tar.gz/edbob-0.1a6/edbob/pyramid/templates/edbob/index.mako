<%inherit file="/base.mako" />
<%def name="menu()"></%def>

<div class="object-index">
  <div class="wrapper">

    <div class="right">
      ${self.menu()|n}
    </div>

    <div class="left">
      ${search.render()|n}
    </div>
  </div>

  ${grid|n}

</div>