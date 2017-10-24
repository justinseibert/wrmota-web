var TouchClick = function(element,callback){
  var symbol = element[0];
  var name = element.substr(1);

  if (symbol == '.'){
    element = document.getElementsByClassName(name);
  } else if (symbol == '#'){
    element = document.getElementById(name);
  }

  if (element.length != 'undefined' && element.length > 0){
    for (var i = 0; i < element.length; i++){
      addTouch(element[i]);
      addClick(element[i]);
    }
  } else {
    addTouch(element);
    addClick(element);
  }

  function addTouch(elem){
    var move = false;
    elem.addEventListener('touchmove', function(evt){
      move = true;
    })
    elem.addEventListener('touchend', function(evt){
      if (!move){
        evt.preventDefault();
        elem.click();
      }
    })
  }

  function addClick(elem){
    elem.addEventListener('click', function(evt){
      callback(elem);
    })
  }
}
