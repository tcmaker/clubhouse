$(function () {
  $('#id_contact_id').on('input', function() {
    $.get(
      $("#import-preview").data('ajax'),
      {contact_id: $(this).val()}
    ).done(function(data) {
      var data = JSON.stringify(data, null, 2);
      $('#import-preview').html(data);
    }).fail(function() {
      $('#import-preview').html('Bad {{ request.user.first_name }}! You typed an invalid contact ID.');
    });
  });
});
