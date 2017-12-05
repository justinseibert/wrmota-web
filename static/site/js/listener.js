/**
 * Construct Listener to listen for events and call functions, currently supports resize and load events
 *
 * @param {object} args                 - object currently includes resize object with options for functions to call during resize event, and load object with options for functions to call during document load event
 * @param {string} args.resizeContainer - element that should trigger the resize event callbacks
 * @default window
 * @param {number} args.resizeTimer     - integer value to time to wait between resize callback, prevents overdoing it...
 * @default 500 (ms)
 * @param {array} args.resizeFunctions  - array of functions to call when resize is triggered
 * @default false                       - for when other event listeners get added and resize is not desired
 * @param {string} args.loadState       - detecting document readyState (loading, interactive, complete)
 * @default complete
 * @param {array} args.loadFunctions    - array of functions to call when document readyState changes
 */

var Listener = function(args){
  var lsn = this || {};
  lsn.func = {
    'resize' : {
      'container' : (args.resizeContainer == undefined) ? window : args.resizeContainer,
      'timer' : (args.resizeTimer == undefined) ? 500 : args.resizeTimer,
      'functions' : (args.resizeFunctions == undefined) ? false : args.resizeFunctions
    },
    'load' : {
      'state' : (args.loadState == undefined) ? 'complete' : args.loadState,
      'functions' : (args.loadFunctions == undefined) ? false : args.loadFunctions
    }
  }

  var timer;
  lsn.resize = function(){
    window.clearTimeout(timer);
    timer = window.setTimeout(function(){
      lsn.do('resize');
    }, lsn.func.resize.timer);
  };

  lsn.load = function(){
    if( document.readyState == lsn.func.load.state ){
      lsn.do('load');
    }
  }

  lsn.do = function(it){
    for(var i in lsn.func[it].functions){
      lsn.func[it].functions[i]();
    }
  }

  if (lsn.func.resize.functions) {
    lsn.func.resize.container.addEventListener('resize', lsn.resize);
  }
  if (lsn.func.load.functions) {
    document.addEventListener('readystatechange', lsn.load);
  }
}

/**
  *  @example *
  function Interactive(){
    console.log('i am interactive');
  }
  function Complete(){
    console.log('i am completely loaded');
  }
  function Size(){
    console.log('i have been resized');
  }
  var x = new Listener({
    resizeFunctions: [Size],
    loadState: 'interactive',
    loadFunctions: [Interactive]
  })

  var y = new Listener({
    loadState: 'complete',
    loadFunctions: [Complete]
  })
 /*
 */
