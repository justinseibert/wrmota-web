var TableData = function(args){
  this.table = null;
  this.name = args.name || null;
  this.data = args.data || null;
  this.url = args.url || null;
  this.hide = args.hide || false;
  this.crop = args.crop || false;
  this.rmCols = args.rmCols || [];
  this.columns = args.columns || [];
  this.input = args.input || '#table-search';

  if (this.data != null && this.url == null){
    this.create();
  } else {
    this.name = 'default';
    var $this = this;
    $.ajax({
      type: "GET",
      url: this.url,
      success: function(data) {
        $this.data = data;
        $this.ajaxCreate();
        console.log(data);
      },
      error: function(data){
        console.log(data);
      }
    });
  }
}

TableData.prototype.ajaxCreate = function(){
  var id = '#'+this.name+'Table';
  var $this = this;
  this.data.head.forEach(function(col){
    if (!$this.rmCols.includes(col)){
      $this.columns.push({
        'data': col,
        'title': col
      });
    }
  })
  // hello
  this.table = $(id).DataTable({
    data: this.data.data,
    columns: this.columns,
    paging: false,
    scrolling: false,
    dom: 'ltr',
    crop: true,
  });

  if (this.crop){
    var head = $('#tableHeader').outerHeight(true);
    $(id+'_wrapper')
      .css('height', window.innerHeight - head)
      ;
    $(id)
      .addClass('overflow-container')
      .css('height', window.innerHeight - head)
      ;
  }

  var table = this.table;
  $(this.input).on('keyup', table, function(){
    table.search(this.value).draw();
  })
}

TableData.prototype.create = function(){
  var id = '#'+this.name+'Table';
  this.table = $(id).DataTable({
    paging: false,
    scrolling: false,
    dom: 'ltr',
  });
  if (this.hide){
    $(id+'_wrapper').addClass('u-hide');
  }
  if (this.crop){
    var head = $('#tableHeader').outerHeight(true);
    // var foot = $(id+'_info').outerHeight(true);
    // console.log(window.innerHeight,head,foot);
    $(id+'_wrapper')
      .css('height', window.innerHeight - head)
      ;
    $(id)
      .addClass('overflow-container')
      .css('height', window.innerHeight - head)
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
}

TableData.prototype.show = function(){
  id = '#'+this.name+'Table_wrapper';
  $('.dataTables_wrapper').removeClass('u-hide').addClass('u-hide');
  $(id+', #tableName').removeClass('u-hide')
  $('#tableName b').html(this.name);
}

TableData.prototype.get_entry = function(el){
  var id = el.dataset.id;
  for (var each in this.data){
    if (this.data[each].id == id){
      return this.data[each];
    }
  }
}

TableData.prototype.get_all = function(col){
  entries = [];
  for (var each in this.data){
    entries.push(this.data[each][col]);
  }
  return entries;
}
