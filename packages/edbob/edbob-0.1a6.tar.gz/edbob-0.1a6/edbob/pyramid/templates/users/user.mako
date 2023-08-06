<%inherit file="/users/base.mako" />
<%inherit file="/crud.mako" />

<%def name="crud_name()">User</%def>

<%def name="menu()">
  <p>${h.link_to("Back to Users", url('users.list'))}</p>
</%def>

${parent.body()}
