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
  this.editable = args.editable || [];
  this.permission = args.permission || 0;
  this.editCallback = args.editCallback || null;
  this.cells = {
    current: null,
    active_id: null,
    data: null,
    clicked: null,
    input: null,
    allowed: false,
  }

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
    buttons: [
      {
        extend: 'csv',
        text: 'Export CSV'
      },
      {
        extend: 'collection',
        text: 'Show/Hide Columns',
        buttons: [{
          extend: 'columnsToggle',
          className: 'custom-spacing',
        }],
        autoClose: false,
        fade: 0
      }
    ],
    crop: true,
    fixedHeader: true,
    columnDefs: [{
      targets: '_all',
      createdCell: function(td, cellData, rowData, row, col){
        if (self.ajaxPass > 0){
          td.dataset.uid = row*col;
          td.dataset.id = rowData.id;
          td.dataset.value = cellData;
          td.dataset.col = self.columns[col].data;
          if (self.editable.includes(self.columns[col].data)){
            td.dataset.editable = 1;
          }
        }
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
    self.table.search(this.value).draw();
  });

  $(id+' tbody').on('click', 'tr', function(el){
    if (self.rowClickCallback){
      self.rowClickCallback(el.target.dataset, el);
    }
    if (self.editable.length > 0 && self.permission > 0){
      self.edit(el.target.dataset, el);
    }
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

TableData.prototype.edit = function(data,el){
  let self = this;
  let cells = self.cells;
  let allowed_edits = self.editable;

  cells.clicked = el;
  cell_activation(true);

  if (cells.allowed && el.target.tagName == 'TD'){
    // create input area with existing cell data
    let original = el.target.innerHTML;
    el.target.innerHTML = '';

    cells.input = document.createElement('input');
    cells.input.type = "text";
    cells.input.value = original;
    el.target.appendChild(cells.input);

    cells.input.select();
    cells.input.addEventListener('keydown', confirm_edit)
  }

  function confirm_edit(e){
    console.log(cells.allowed);
    if (e.key == 'Enter'){
      cells.input.removeEventListener('keydown', confirm_edit);
      cell_activation(false);
    }
  }

  function cell_activation(activate){
    if (activate){
      // if a cell was clicked previously, only set editable if newly clicked is cell
      if (cells.current && cells.clicked.target.tagName == 'TD') {
        write_value();
        cells.current = cells.clicked;
        cells.data = cells.current.target.dataset;
        cells.active_id = cells.data.uid;
      } else if (!cells.current){
        // if none selected, set current editable to clicked cell
        cells.current = cells.clicked;
        cells.data = cells.current.target.dataset;
        cells.active_id = cells.data.uid;
      }
      check_allowance();
    } else {
      write_value();
      cells.current = false;
      cells.active_id = null;
      cells.clicked = null;
      cells.uid = null;
      cells.input = null;
    }
  }

  function write_value(){
    // if allowed to edit
    if (cells.allowed){
      let val = cells.current.target.firstChild.value;
      cells.current.target.innerHTML = val;
      // send edited data to local callback function with (database row, column, input value)
      self.editCallback(self.data[cells.data.id], cells.data.col, val);
    }
  }

  function check_allowance(){
    if (allowed_edits.includes(cells.data.col)){
      cells.allowed = true;
    } else {
      cells.allowed = false;
    }
  }
}
