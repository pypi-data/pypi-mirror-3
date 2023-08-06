<%inherit file="/base.mako" />

<%def name="title()">Login</%def>

<%def name="head_tags()">
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/login.css'))}
</%def>

${h.image(logo_url, "${self.global_title()} logo", id='login-logo', **logo_kwargs)}

<div class="fieldset">
  ${h.form('')}
##  <input type="hidden" name="login" value="True" />
  <input type="hidden" name="referer" value="${referer}" />

  % if error:
      <div class="error">${error}</div>
  % endif

  <div class="field-couple">
    <label for="username">Username:</label>
    <input type="text" name="username" id="username" value="" />
  </div>

  <div class="field-couple">
    <label for="password">Password:</label>
    <input type="password" name="password" id="password" value="" />
  </div>

  <div class="buttons">
    ${h.submit('submit', "Login")}
    <input type="reset" value="Reset" />
  </div>

  ${h.end_form()}
</div>

<script language="javascript" type="text/javascript">

$(function() {

    $('form').submit(function() {
	if (! $('#username').val()) {
	    with ($('#username').get(0)) {
		select();
		focus();
	    }
	    return false;
	}
	if (! $('#password').val()) {
	    with ($('#password').get(0)) {
		select();
		focus();
	    }
	    return false;
	}
	return true;
    });

    $('#username').focus();

});

</script>
