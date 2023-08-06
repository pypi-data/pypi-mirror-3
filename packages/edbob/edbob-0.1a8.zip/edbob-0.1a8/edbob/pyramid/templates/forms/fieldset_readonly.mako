<table class="fieldset ${class_}">
  <tbody>
    %for field in fieldset.render_fields.itervalues():
	%if field.requires_label:
	    <tr class="${field.key}">
	      <td class="label">${field.label()|h}</td>
	      <td>${field.render_readonly()|n}</td>
	    </tr>
	%endif
    %endfor
  </tbody>
</table>