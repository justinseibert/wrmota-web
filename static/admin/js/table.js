var TableData = function(args){
  this.table = null;
  this.name = args.name || null;
  this.data = args.data || null;
  this.hide = args.hide || false;
  this.crop = args.crop || false;
  this.rmCols = args.rmCols || [];
  this.input = args.input || '#table-search';

  this.create()
}

TableData.prototype.create = function(){
  var id = '#'+this.name+'Table';
  this.table = $(id).DataTable({
    paging: false,
    scrolling: false,
    dom: 'ltir',
  });
  if (this.hide){
    $(id+'_wrapper').addClass('u-hide');
  }
  if (this.crop){
    var head = $('#tableHeader').outerHeight(true);
    var foot = $(id+'_info').outerHeight(true);
    console.log(head,foot);
    $(id+'_wrapper')
      .css('height', window.innerHeight - head)
      ;
    $(id)
      .addClass('overflow-container')
      .css('height', window.innerHeight - head - foot)
      ;
  }
  var rmCol = this.rmCols.length;
  if (rmCol > 0){
    for (var i = 0; i < rmCol; i++){
      $('.access-col_'+this.rmCols[i]).addClass('u-hide');
    }
  }

  var table = this.table;
  $(this.input).on('keyup', table, function(){
    table.search(this.value).draw();
  })
},

TableData.prototype.show = function(name){
  id = '#'+name+'Table_wrapper';
  $('.dataTables_wrapper').removeClass('u-hide').addClass('u-hide');
  $(id+', #tableName').removeClass('u-hide')
  $('#tableName b').html(name);
}
