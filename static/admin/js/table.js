var TableData = function(args){
  this.table = null;
  this.name = args.name || null;
  this.data = args.data || null;
  this.url = args.url || null;
  this.hide = args.hide || false;
  this.crop = args.crop || false;
  this.rmCols = args.rmCols || [];
  this.columns = args.columns || [{data: 'id', title: 'id'}];
  this.buttons = args.buttons || [];
  this.input = args.input || '#table-search';
  this.callback = args.callback || false;
  this.rowClickCallback = args.rowClickCallback || null;
  this.ajaxPass = 0;

  if (this.url == null){
    this.htmlCreate();
  } else {
    this.ajaxCreate();
  }
}

TableData.prototype.htmlCreate = function(){
  var id = '#'+this.name+'Table';
  console.log(id);
  this.table = $(id).DataTable({
    paging: false,
    scrolling: false,
    dom: 'ltr',
    rowId: 'id',
  });
  if (this.hide){
    $(id+'_wrapper').addClass('u-hide');
  }
  var rmCol = this.rmCols.length;
  if (rmCol > 0){
    for (var i = 0; i < rmCol; i++){
      $('.access-col_'+this.rmCols[i]).addClass('u-hide');
    }
  }
  this.setupTable(id);
}

TableData.prototype.ajaxCreate = function(){
  var self = this;
  var id = '#defaultTable';
  $(id).html('');
  self.table = $(id).DataTable({
    ajax: {
      url: self.url,
      dataSrc: 'data'
    },
    deferRender: true,
    columns: self.columns,
    paging: false,
    scrolling: false,
    dom: 'Bltr',
    buttons: ['csv','colvis'],
    crop: true,
    fixedHeader: true,
    columnDefs: [{
      targets: '_all',
      createdCell: function(td, cellData, rowData, row, col){
        td.dataset.id = rowData.id;
        td.dataset.value = cellData;
      }
    }],
    createdRow: function(row, data, dataIndex){
      row.dataset.id = data.id;
    },
    initComplete: function(settings, data){
      self.renderColumns(settings,data);
    }
  });

  if (self.ajaxPass > 0){
    self.setupTable(id);
  }
}

TableData.prototype.setupTable = function(id){
  var self = this;

  self.table.buttons().container().appendTo($('#colVisRow'));

  if (self.crop){
    var head = $('#tableHeader').outerHeight(true);
    $(id+'_wrapper')
    .css('height', window.innerHeight - head)
    ;
    $(id)
    .addClass('overflow-container')
    .css('height', window.innerHeight - head)
    ;
  }


  $(self.input).on('keyup', self.table, function(){
    table.search(this.value).draw();
  });

  $(id+' tbody').on('click', 'tr', function(el){
    self.rowClickCallback(el.target.dataset);
  })

};

TableData.prototype.renderColumns = function(settings,data){
  var self = this;
  if (self.ajaxPass < 1){
    self.columns = [];
    self.ajaxPass++;
    data.head.forEach(function(col){
      if (!self.rmCols.includes(col)){
        self.columns.push({
          'data': col,
          'title': col
        });
        self.buttons.push(col);
      }
    });
    self.data = data.data;
    self.table.clear();
    self.table.destroy();
    self.ajaxCreate();
  } else if (self.callback){
    self.callback(self.data);
  }
};


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

TableData.prototype.get_entry_v2 = function(el){
  var id = el.id;
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
