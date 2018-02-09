// function ValidateEmail(el,e){
//   e.preventDefault();
//   var user_email = document.getElementById('UserEmail').value;
//   if (user_email != '' && user_email.indexOf('@') > -1){
//     recaptcha_func = SubmitEmail;
//     grecaptcha.execute();
//   } else {
//     alert('an email is required');
//   }
// }
// function SubmitEmail(){
//   var url = "/api/subscribe";
//   var message = '';
//   $('#AJAXAlert').addClass('u-hide');
//   $.ajax({
//       type: "POST",
//       url: url,
//       data: $('#EmailSubmitForm').serialize(),
//       success: function(data) {
//         if (data.errors){
//           $('#AJAXAlert').addClass('failure');
//           message = 'that didn\'t work';
//         } else {
//           $('#AJAXAlert').addClass('success');
//           message = 'success! be on the lookout for emails from <i>'+data.from+'</i>';
//         }
//         $('#AJAXAlert').html(message);
//         $('#AJAXAlert').addClass('success');
//         $('#AJAXAlert').removeClass('u-hide');
//       },
//       error: function(data){
//         $('#AJAXAlert').html('oops, that didn\'t work for some reason');
//         $('#AJAXAlert').addClass('failure');
//         $('#AJAXAlert').removeClass('u-hide');
//       }
//   });
// }

var EmailForm = function(args){
  this.form = args.form || $('#EmailSubmitForm');
  this.user_email = args.user_email || $('#UserEmail');
  this.alert_box = args.alert_box || $('#AJAXAlert');
  this.subscribe_url = args.subscribe_url || 'api/subscribe';
}

EmailForm.prototype.validate = function(){
  var email = this.user_email.val();
  if (email != '' && email.indexOf('@') > -1){
    recaptcha_pass = this;
    grecaptcha.execute();
  } else {
    alert('an email is required');
  }
}

EmailForm.prototype.submit = function(){
  var form = this.form;
  var url = this.subscribe_url;
  var alertbox = this.alert_box;
  var message = '';

  form.addClass('u-hide');
  $.ajax({
      type: "POST",
      url: url,
      data: form.serialize(),
      success: function(data) {
        if (data.errors){
          alertbox.addClass('failure');
          message = 'that didn\'t work';
        } else {
          alertbox.addClass('success');
          message = 'success! be on the lookout for emails from <i>'+data.from+'</i>';
        }
        alertbox.html(message);
        alertbox.addClass('success');
        alertbox.removeClass('u-hide');
        form.removeClass('u-hide');
      },
      error: function(data){
        alertbox.html('oops, that didn\'t work for some reason');
        alertbox.addClass('failure');
        alertbox.removeClass('u-hide');
        form.removeClass('u-hide');
      }
  });
}
