var Brick = function(args){
  var b = this || {};
  var page = document.getElementById('pageBrick');
  var canvas = document.getElementById('canvasBrick');
  b.args = {
    segment: args.segment || 8
  }
  var config = {
    dpi: 96,
    width: 8*96,
    height: 2*96,
    last_width: 8*96,
    print_width: 8*300,
    scale: 1,
    attempt: 0,
  }

  function inch(n){
    var ratio = canvas.width/config.width;
    return n*config.dpi*ratio;
  }

  b.init = function(){
    paper.project.activeLayer.transformContent = false;
    config.last_width = canvas.width;

    b.scale();
    b.draw();
  }

  b.draw = function(){
    var ball = new paper.Shape.Circle(new paper.Point(canvas.width/2, canvas.height/2), canvas.height/2);
    ball.fillColor = 'red';

    var segment = b.args.segment;

    for (var i = 0; i < segment; i++){
      var w = 8/segment;
      var x = inch(w*i)+inch(w/2)
      var r = Math.round((255/segment)*i);
      var g = 255-r;
      console.log(r,g);

      var path = new paper.Path();
      path.strokeColor = 'rgb('+r+','+g+','+r+')';
      path.strokeWidth = inch(w);

      var start = new paper.Point(x, inch(0.25));
      path.moveTo(start);
      path.lineTo(start.add([ 0, inch(1.5) ]));
    }

    paper.view.draw();
  }

  b.scale = function(){
    var current = canvas.width;
    console.log(current);
    var scale = current/config.last_width;

    config.last_width = current;
    config.scale = scale;

    canvas.height = (current/config.width)*config.height;
    paper.project.activeLayer.scale(scale, [0,0]);
  }

  b.print = function(){
    canvas.width = config.print_width;
    b.scale();
    if (config.attempt < 5){
      config.attempt++;
      wait(100,print);
    } else {
      alert('printing encountered an error');
      config.attempt = 0;
    }
  }

  var timer;
  var wait = function(time,callback){
    window.clearTimeout(timer);
    timer = window.setTimeout(function(){
      callback()
    }, time);
  };

  var print = function(){
    var cache_title = document.title;
    if (canvas.width == config.print_width){
      document.title = 'wrmota_'+(+new Date).toString(36);
      window.print();
      canvas.width = canvas.clientWidth;
      b.scale();
      document.title = cache_title;
    } else {
      b.print();
    }
  }

  paper.setup(canvas);
  paper.view.onResize = function(event){
    b.scale();
  }
}
