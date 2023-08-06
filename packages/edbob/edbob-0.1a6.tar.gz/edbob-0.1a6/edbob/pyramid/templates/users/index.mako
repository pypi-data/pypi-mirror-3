<%inherit file="/users/base.mako" />
<%inherit file="/index.mako" />

<%def name="title()">Users</%def>

<%def name="menu()">
  <p>${h.link_to("Create a new User", url('user.new'))}</p>
</%def>

${parent.body()}
