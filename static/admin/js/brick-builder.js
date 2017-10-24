var Brick = function(args){
  var user = this || {};
  var page = document.getElementById('pageBrick');
  var canvas = document.getElementById('canvasBrick');
  var map = document.getElementById('canvasMap');
  var selectButton = document.getElementById('chooseTwo');
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
      margin: [
        [0.25,0.25],[4,0.25],[7.75,0.25],
        [0.25,1.75],[4,1.75],[7.75,1.75],
      ],
      // start: [
      //   [0,0],[2,0],[4,0],[6,0],[8,0],
      //   [0,2],[2,2],[4,2],[6,2],[8,2],
      // ],
      // margin: [
      //   [0.25,0.25],[2,0.25],[4,0.25],[6,0.25],[7.75,0.25],
      //   [0.25,1.75],[2,1.75],[4,1.75],[6,1.75],[7.75,2],
      // ],
      bounds: {
        x: [0.25,7.75],
        y: [0.25,1.75],
      }
    },
    used: {},
    map_layers: 0,
    edit_layer: false,
    stroke: 0.25,
    hits: {
    	segments: true,
    	stroke: true,
      fill: true,
    	tolerance: 5
    },
    ball: null,
    paper: {
      brick: null,
      map: null,
    }
  }

  var hit = {
    path: null,
    segment: null,
    dragging: false,
  }

  args = args || {};
  user.args = {
    segment: args.segment || 8,
    points: {
      id: {},
      selected: []
    },
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

      paper.view.scale(scale,[0,0]);
      // console.log(paper.view.bounds);
      // paper.project.activeLayer.bounds.size.width = canvas.width;
      // paper.project.activeLayer.bounds.size.height = canvas.height;
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
    activate: function(canvas){
      var c = config.paper[canvas];
      paper.projects[c].activate();
    }
  }

  var valid = {
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
    },
    bounds: function(x,y){
      var bounds = config.points.bounds;
      var coord = {
        bottom: bounds.y[0],
        top: bounds.y[1],
        left: bounds.x[0],
        right: bounds.x[1],
      }
      if (x < coord.left)
        x = coord.left;
      if (x > coord.right)
        x = coord.right;
      if (y < coord.bottom)
        y = coord.bottom;
      if (y > coord.top)
        y = coord.top;

      return {
        x: x,
        y: y
      };
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
    any: function(scope){

      util.activate('brick');
      paper.projects[0].clear();

      var p;
      if (!config.edit_layer){
        p = util.chooseTwo();
        user.args.points.selected = [p.a,p.b];
      } else {
        p = {
          a: user.args.points.selected[0],
          b: user.args.points.selected[1],
        }
        config.edit_layer = false;
        config.hits.stroke = true;
      }
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

      var from = new paper.Point(0, 0);
      var size = new paper.Size(canvas.width,canvas.height);
      var mask = new paper.Path.Rectangle(from, size);
      var rect = new paper.Path.Rectangle(from, size);
      rect.fillColor = 'hsl('+util.randInt(255)+',100%,75%)';

      var path = new paper.Path();
      path.strokeColor = 'white';
      path.strokeWidth = config.stroke;
      path.strokeJoin = 'round';
      path.strokeCap = 'round';

      path.moveTo(start.a);
      path.lineTo(margin.a);
      path.lineTo(random.a);
      // path.lineTo(random.b);
      path.lineTo(margin.b);
      path.lineTo(start.b);

      var grouped = new paper.Group(mask,rect,path);
      // grouped.clipped = true;
    },
    map: function(){
      util.activate('brick');
      var map = paper.projects[config.paper.map];
      // var layer = map.addLayer(new paper.Layer());
      paper.project.activeLayer.children[0].copyTo(map);

      // console.log(map.layers);
      var child = map.activeLayer.children[config.map_layers];
      child.applyMatrix = false;
      child.scale(0.25);

      var margin = util.inch(0.0625);
      var row = Math.ceil((config.map_layers+1)/4) -1;
      console.log(row%2, config.map_layers);
      child.position.x = margin*(config.map_layers%4) + (child.bounds.width*(config.map_layers%4)) + child.bounds.width*(1-row%2/2);
      child.position.y = child.bounds.height*row + margin*row + child.bounds.height/2;

      config.map_layers++;
      user.draw.any();
    },
    points: function(){
      if (!config.edit_layer){
        config.edit_layer = true;
        config.hits.stroke = false;
        selectButton.innerHTML = 'done';
        console.log(selectButton.innerHtml);

        new paper.Layer();
        paper.project.activeLayer.name = 'temp';
        var from = new paper.Point(0, 0);
        var size = new paper.Size(canvas.width,canvas.height);
        var mask = new paper.Path.Rectangle(from, size);
        mask.fillColor = 'rgba(255,255,255,0.8)';

        var circle = [];
        for (var i = 0; i < config.points.start.length; i++){
          circle[i] = new paper.Path.Circle(new paper.Point(config.points.margin[i]), util.inch(0.1));
          circle[i].fillColor = 'black';
          circle[i].strokeColor = 'black';
          circle[i].strokeWidth = util.inch(0.05);
          user.args.points.id[circle[i].id] = i;
          circle[i].name = i+'_circle_selector';
        }

        var select = user.args.points.selected;
        for (var i = 0; i < select.length; i++){
          circle[select[i]].fillColor = 'white';
        }
      } else {
        selectButton.innerHTML = 'select';
        paper.project.layers['temp'].remove();
        user.draw.any();
      }
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
        hit.segment = valid.drag() ? result.segment : null
        if (event.modifiers.shift && hit.segment){
          hit.segment.remove();
        }
      } else if (result.type == 'stroke') {
        hit.segment = valid.add() ? hit.path.item.insert(result.location.index + 1, event.point) : null;
      } else if (result.type == 'fill' && result.item.name.indexOf('circle_selector') > 0){
        var p = user.args.points;
        console.log(p.selected);
        if (result.item.fillColor.equals('black')){
          result.item.fillColor = 'white';
          var black = p.selected[1]+'_circle_selector';
          paper.project.layers['temp'].children[black].fillColor = 'black';
          p.selected[1] = p.selected[0];
          p.selected[0] = p.id[result.item.id];
          console.log(p.selected);
        }
      }
    }
  }

  action.onMouseDrag = function(event) {
    var mouse = event.point;
    var bounds = valid.bounds(mouse.x,mouse.y);
    if(hit.segment){
  		hit.segment.point.x = bounds.x;
  		hit.segment.point.y = bounds.y;
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
    paper.setup(canvas);
    config.paper.brick = paper.project.index;
    paper.setup(map);
    config.paper.map = paper.project.index;

    paper.project.activeLayer.applyMatrix = false;
    config.last_width = canvas.width;
    util.scale();

    config.points.start = config.points.start.map(util.inch);
    config.points.margin = config.points.margin.map(util.inch);
    config.points.bounds.x = config.points.bounds.x.map(util.inch);
    config.points.bounds.y = config.points.bounds.y.map(util.inch);
    config.stroke = util.inch(config.stroke);

    // config.ball = new paper.Shape.Circle(new paper.Point(-100,-100), util.inch(0.1));
    // config.ball.fillColor = 'red';

    user.draw.any(canvas);
  }
  init();


  paper.view.onResize = function(event){
    util.wait(100,util.scale);
  }
}
