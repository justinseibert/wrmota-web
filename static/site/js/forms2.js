var wrmotaForm = function(args){
  this.form = args.form || null;
  this.validate_items = args.validate_items || [];
  this.alert_box = args.alert_box || $('#AJAXAlert');
  this.submit_url = args.submit_url || null;
  this.recaptcha = args.recaptcha;
}

wrmotaForm.prototype.validate = function(){
  var valid = false;
  var invalid = '';
  var items = this.validate_items;
  for (var i = 0, j = items.length; i < j; i++){
    var rule = items[i][0];
    var input = items[i][1].val();
    valid = this.validation[rule](input);
    if (!valid) {
      invalid += items[i][1].attr('name')+', ';
    }
  }

  if (invalid.indexOf(',') > -1){
    invalid = invalid.slice(0,-2);
    var data = {
      errors: true,
      message: 'Invalid input for '+invalid
    }
    this.showMessage(data);
  } else {
    if (this.recaptcha){
      recaptcha_pass = this;
      grecaptcha.execute();
    } else {
      this.submit();
    }
  }
}

wrmotaForm.prototype.validation = {
  safe: function(val){
    var hasInput = val.length > 0;
    var notWeird = val.search(/[:;]/) == -1
    return (hasInput && notWeird) ? true : false;
  },
  text: function(val){
    var hasInput = val.length > 0;
    var notWeird = val.search(/[:;.,<>?\/\\`~@#$%^&*\(\)!\{\}\[\]+=-]/) == -1
    return (hasInput && notWeird) ? true : false;
  },
  email: function(val){
    var hasInput = val.length > 0;
    var hasAt = val.indexOf('@') > -1;
    return (hasInput && hasAt) ? true : false;
  },
  password: function(val){
    var has16chars = val.length >= 16;
    var hasNumber = val.search(/[0-9]/g) > -1;
    var hasUppercase = val.search(/[A-Z]/g) > -1;
    var hasLowercase = val.search(/[a-z]/g) > -1;
    return (has16chars && hasNumber && hasUppercase && hasLowercase) ? true : false;
  }
}

wrmotaForm.prototype.showMessage = function(data){
  var a = this.alert_box;
  a.addClass('u-hide');
  var t = window.setTimeout(function(){
    if (data.errors){
      a.removeClass('success');
      a.addClass('failure');
    } else {
      a.removeClass('failure');
      a.addClass('success');
    }
    a.html(data.message);
    a.removeClass('u-hide');
  }, 50);
}

wrmotaForm.prototype.submit = function(){
  var f = this;
  f.form.addClass('u-hide');

  $.ajax({
      type: "POST",
      url: f.submit_url,
      data: f.form.serialize(),
      success: function(data) {
        f.showMessage(data);
        f.form.removeClass('u-hide');
        if(data.errors){
          console.log(data.errors);
        }
        if(data.log){
          console.log(data.log);
        }
      },
      error: function(data){
        f.alert_box.html('oops, that didn\'t work for some reason');
        f.alert_box.addClass('failure');
        f.alert_box.removeClass('u-hide');
        f.form.removeClass('u-hide');
        console.log(data.errors);
      }
  });
}
