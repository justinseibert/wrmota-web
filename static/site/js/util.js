function Util(args){
  args = args || {};
};

Util.prototype.random = function(min,max){
  return Math.floor(Math.random() * (max-min+1)) + min;
}

Util.prototype.chance = function(percent=0.5){
  return (Math.random() <= percent) ? {bool:true,num:1} : {bool:false,num:-1};
}

Util.prototype.fillEmptyArray = function(n){
  return Array.apply(null, Array(n)).map(Number.prototype.valueOf,0);
};

Util.prototype.fetchImage = function(url){
  return new Promise(function(resolve, reject) {
    // Standard XHR to load an image
    var request = new XMLHttpRequest();
    request.open('GET', url);
    request.responseType = 'blob';
    // When the request loads, check whether it was successful
    request.onload = function() {
      if (request.status === 200) {
      // If successful, resolve the promise by passing back the request response
      let img = new Image();
      img.src = window.URL.createObjectURL(request.response);
      // resolve after img object has been loaded
      img.onload = function(){
        // release ObjectURL
        resolve(img);
        // window.URL.revokeObjectURL(img.src);
      }
      } else {
      // If it fails, reject the promise with a error message
        reject(Error('Image didn\'t load successfully; error code:' + request.statusText));
      }
    };
    request.onerror = function() {
    // Also deal with the case when the entire request fails to begin with
    // This is probably a network error, so reject the promise with an appropriate message
        reject(Error('There was a network error.'));
    };
    // Send the request
    request.send();
  });
};

Util.prototype.getData = function(url){
  return new Promise(function(resolve, reject) {
    // Standard XHR to load an image
    var request = new XMLHttpRequest();
    request.open('GET', url);
    request.responseType = 'json';
    request.setRequestHeader('Cache-Control', 'max-age=0');
    // When the request loads, check whether it was successful
    request.onload = function() {
      if (request.status === 200) {
      // If successful, resolve the promise by passing back the request response
        resolve(request.response);
      } else {
      // If it fails, reject the promise with a error message
        reject(Error('GET failed with error code:' + request.statusText));
      }
    };
    request.onerror = function() {
    // Also deal with the case when the entire request fails to begin with
    // This is probably a network error, so reject the promise with an appropriate message
        reject(Error('There was a network error.'));
    };
    // Send the request
    request.send();
  });
};

Util.prototype.postData = function(url, data, csrf='', asForm=false) {
  return new Promise(function(resolve, reject) {
    var request = new XMLHttpRequest();
    request.open('POST', url);
    request.responseType = 'json';
    request.setRequestHeader("X-CSRFToken", csrf);
    request.onload = function() {
      if (request.status === 200) {
        resolve(request.response);
      } else {
        reject(Error('POST failed with error code:' + request.statusText));
      }
    };
    request.onerror = function() {
        reject(Error('There was a network error.'));
    };
    if (!asForm){
      request.setRequestHeader("Content-Type", "application/json");
      request.send(JSON.stringify(data));
    } else {
      let form = new FormData();
      for (let key in data){
        form.append(key, data[key]);
      }
      request.send(form);
    }
  });
};
