<%inherit file="/roles/base.mako" />
<%inherit file="/index.mako" />

<%def name="title()">Roles</%def>

<%def name="menu()">
  <p>${h.link_to("Create a new Role", url('role.new'))}</p>
</%def>

${parent.body()}
