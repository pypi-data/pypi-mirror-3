<%inherit file="/people/base.mako" />
<%inherit file="/index.mako" />

<%def name="title()">People</%def>

<%def name="menu()">
  % if request.has_perm('people.create'):
      <p>${h.link_to("Create a new Person", url('person.new'))}</p>
  % endif
</%def>

${parent.body()}
