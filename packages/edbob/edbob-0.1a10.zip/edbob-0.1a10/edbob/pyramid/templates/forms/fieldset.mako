<% _focus_rendered = False %>

<div class="fieldset-form ${class_}">
  ${h.form(fieldset.action_url+('?uuid='+fieldset.model.uuid) if fieldset.edit else '', enctype='multipart/form-data')}

  % for error in fieldset.errors.get(None, []):
      <div class="fieldset-error">${error}</div>
  % endfor

  % for field in fieldset.render_fields.itervalues():

      <div class="field-wrapper ${field.name}">
        % for error in field.errors:
            <div class="field-error">${error}</div>
        % endfor
        ${field.label_tag()|n}
        <div class="field">
          ${field.render()|n}
        </div>
        % if 'instructions' in field.metadata:
            <span class="instructions">${field.metadata['instructions']}</span>
        % endif
      </div>

      % if (fieldset.focus == field or fieldset.focus is True) and not _focus_rendered:
          % if not field.is_readonly():
              <script language="javascript" type="text/javascript">
                $(function() {
                    $('#${field.renderer.name}').focus();
                });
              </script>
              <% _focus_rendered = True %>
          % endif
      % endif

  % endfor

  % if fieldset.allow_continue:
      <div class="checkbox">
        ${h.checkbox('add-another', checked=True)}
        <label for="add-another">Add another after this one</label>
      </div>
  % endif

  <div class="buttons">
    ${h.submit('submit', "Save")}
    <button type="button" class="cancel">Cancel</button>
  </div>
  ${h.end_form()}
</div>

<script language="javascript" type="text/javascript">
  $(function() {
      $('button.cancel').click(function() {
          location.href = '${fieldset.home_url}';
      });
  });
</script>
