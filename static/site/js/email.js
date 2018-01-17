function ValidateEmail(el,e){
  e.preventDefault();
  var user_email = document.getElementById('UserEmail').value;
  if (user_email != '' && user_email.indexOf('@') > -1){
    grecaptcha.execute();
  } else {
    alert('an email is required');
  }
}
function SubmitEmail(){
  var url = "/api/subscribe";
  var message = '';
  $('#AJAXAlert').addClass('u-hide');
  $.ajax({
      type: "POST",
      url: url,
      data: $('#EmailSubmitForm').serialize(),
      success: function(data) {
        if (data.errors){
          $('#AJAXAlert').addClass('failure');
          message = 'that didn\'t work';
        } else {
          $('#AJAXAlert').addClass('success');
          message = 'success! be on the lookout for emails from <i>'+data.from+'</i>';
        }
        $('#AJAXAlert').html(message);
        $('#AJAXAlert').addClass('success');
        $('#AJAXAlert').removeClass('u-hide');
      },
      error: function(data){
        $('#AJAXAlert').html('oops, that didn\'t work for some reason');
        $('#AJAXAlert').addClass('failure');
        $('#AJAXAlert').removeClass('u-hide');
      }
  });
}
