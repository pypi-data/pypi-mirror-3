<div id="${fieldname}-container" class="autocomplete-container">
  ${h.hidden(fieldname, id=fieldname, value=fieldvalue)}
  ${h.text(fieldname+'-textbox', id=fieldname+'-textbox', value=display,
      class_='autocomplete-textbox', style='display: none;' if fieldvalue else '')}
  <div id="${fieldname}-display" class="autocomplete-display"${'' if fieldvalue else ' style="display: none;"'|n}>
    <span>${display}</span>
    <button type="button" id="${fieldname}-change" class="autocomplete-change">Change</button>
  </div>
</div>
<script language="javascript" type="text/javascript">
$(function() {
    var ${autocompleter} = $('#${fieldname}-textbox').autocomplete({
    serviceUrl: '${service_url}',
    width: '${width}',
    onSelect: function(value, data) {
        $('#${fieldname}').val(data);
        $('#${fieldname}-display span').text(value);
        $('#${fieldname}-textbox').hide();
        $('#${fieldname}-display').show();
        % if callback:
            ${callback}(value, data);
        % endif
    },
    });
});
</script>
