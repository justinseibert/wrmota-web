var Brick = function(args){
  var user = this || {};
  var page = document.getElementById('pageBrick');
  var canvas = document.getElementById('canvasBrick');
  var action = new paper.Tool();

  var config = {
    dpi: 96,
    width: 8*96,
    height: 2*96,
    last_width: 8*96,
    print_width: 8*300,
    scale: 1,
    attempt: 0,
    timer: 0,
    points: {
      start: [
        [0,0],[4,0],[8,0],
        [0,2],[4,2],[8,2]
      ],
      margin:[
        [0.25,0.25],[4,0.25],[7.75,0.25],
        [0.25,1.75],[4,1.75],[7.75,1.75],
      ]
    },
    stroke: 0.25,
    hits: {
    	segments: true,
    	stroke: true,
    	tolerance: 2
    },
  }

  var hit = {
    path: null,
    segment: null,
    dragging: false,
  }

  args = args || {};
  user.args = {
    segment: args.segment || 8
  }

  var util = {
    inch: function(n){
      var ratio = canvas.width/config.width;
      if (n.length > 1){
        for (var i = 0; i < n.length; i++){
          n[i] = n[i]*config.dpi*ratio;
        }
      } else {
        n = n*config.dpi*ratio;
      }
      return n;
    },
    scale: function(){
      var current = canvas.width;
      var scale = current/config.last_width;

      config.last_width = current;
      config.scale = scale;

      canvas.height = (current/config.width)*config.height;
      paper.project.activeLayer.scale(scale, [0,0]);
    },
    wait: function(time,callback){
      window.clearTimeout(config.timer);
      config.timer = window.setTimeout(function(){
        callback()
      }, time);
    },
    print: function(){
      var cache_title = document.title;
      if (canvas.width == config.print_width){
        document.title = 'wrmota_'+(+new Date).toString(36);
        window.print();
        canvas.width = canvas.clientWidth;
        util.scale();
        document.title = cache_title;
      } else {
        user.print();
      }
    },
    randInt: function(max,min){
      min = min || 0;
      return Math.round(Math.random()*(max-min) + min);
    },
    randFlt: function(max,min){
      min = min || 0;
      return Math.random()*(max-min) + min;
    },
    randPt: function(){
      return [
        util.inch(util.randFlt(0.25,7.75)),
        util.inch(util.randFlt(0.25,1.75)),
      ]
    },
    chooseTwo: function(){
      var pool = config.points.start.length - 1;
      var p1 = util.randInt(pool);
      var p2 = util.randInt(pool);

      config.attempt = 0;
      while (p2 == p1){
        if(config.attempt < 3){
          p2 = util.randInt(pool);
          config.attempt++;
        } else if (p1 > 0) {
          p2 = p1--;
        } else {
          p2 = p1++;
        }
      }
      return {
        a: p1,
        b: p2,
      };
    },
  }

  var allow = {
    drag: function(){
      var point = hit.path.segment.index;
      var first = hit.path.item.firstSegment.index + 1;
      var last = hit.path.item.lastSegment.index - 1;
      if(point > first && point < last){
        return true;
      }
      console.log('point can not be dragged');
      return false;
    },
    add: function(){
      var segment = hit.path.location.index;
      var first = hit.path.item.firstSegment.index;
      var last = hit.path.item.lastSegment.index - 1;
      if(segment != first && segment != last){
        return true;
      }
      console.log('point can not be added');
      return false;
    }
  }

  user.draw = {
    inch: function(){
      var ball = new paper.Shape.Circle(new paper.Point(canvas.width/2, canvas.height/2), canvas.height/2);
      ball.fillColor = 'red';

      var segment = user.args.segment;

      for (var i = 0; i < segment; i++){
        var w = 8/segment;
        var x = util.inch(w*i)+util.inch(w/2)
        var r = Math.round((255/segment)*i);
        var g = 255-r;
        console.log(r,g);

        var path = new paper.Path();
        path.strokeColor = 'rgb('+r+','+g+','+r+')';
        path.strokeWidth = util.inch(w);

        var start = new paper.Point(x, util.inch(0.25));
        path.moveTo(start);
        path.lineTo(start.add([ 0, util.inch(1.5) ]));
      }
    },
    all: function(){
      var p = util.chooseTwo();
      var start = {
        a: config.points.start[p.a],
        b: config.points.start[p.b],
      }
      var margin = {
        a: config.points.margin[p.a],
        b: config.points.margin[p.b],
      }
      var random = {
        a: util.randPt(),
        b: util.randPt(),
      }

      var path = new paper.Path();
      path.strokeColor = 'black';
      path.strokeWidth = config.stroke;
      path.strokeJoin = 'round';
      path.strokeCap = 'round';

      console.log(p.a,p.b);
      // var start = ();
      path.moveTo(new paper.Point(start.a));
      path.lineTo(new paper.Point(margin.a));
      path.lineTo(new paper.Point(random.a));
      // path.lineTo(new paper.Point(random.b));
      path.lineTo(new paper.Point(margin.b));
      path.lineTo(new paper.Point(start.b));
    }
  }

  action.onMouseMove = function(event) {
    paper.project.activeLayer.selected = false;
  	if (event.item){
  		event.item.selected = true;
    }
  }

  action.onMouseDown = function(event) {
  	hit.segment = null;
  	var result = paper.project.hitTest(event.point, config.hits);

  	if (!result){
  		return;
    } else {
      hit.path = result;

      if (result.type == 'segment') {
        hit.segment = allow.drag() ? result.segment : null
        if (event.modifiers.shift && hit.segment){
          hit.segment.remove();
        }
      } else if (result.type == 'stroke') {
        hit.segment = allow.add() ? hit.path.item.insert(result.location.index + 1, event.point) : null;
      }
    }
  }

  action.onMouseDrag = function(event) {
  	if (hit.segment) {
  		hit.segment.point.x += event.delta.x;
  		hit.segment.point.y += event.delta.y;
    }
  }

  user.print = function(){
    canvas.width = config.print_width;
    util.scale();
    if (config.attempt < 5){
      config.attempt++;
      util.wait(100,util.print);
    } else {
      alert('printing encountered an error');
      config.attempt = 0;
    }
  }

  var init = function(){
    paper.project.activeLayer.transformContent = false;
    config.last_width = canvas.width;
    util.scale();

    config.points.start = config.points.start.map(util.inch);
    config.points.margin = config.points.margin.map(util.inch);
    config.stroke = util.inch(config.stroke);

    // user.draw.inch();
    user.draw.all();
  }

  paper.setup(canvas);
  paper.view.onResize = function(event){
    util.scale();
  }
  init();
}
