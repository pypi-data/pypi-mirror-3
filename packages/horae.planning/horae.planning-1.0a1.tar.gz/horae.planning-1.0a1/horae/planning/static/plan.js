var sortable = {
  
  resourcepattern : [/\+\+resource\+\+(\d+)/, /\/global_resources\/(\d+)/],
  ids : [],
  forecast : false,
  resource : false
  
};

(function($) {
  
  sortable.init = function(container) {
    table = container.find('.listing.plan');
    if(!table.size())
      return;
    for(var i=0; i<sortable.resourcepattern.length; i++) {
      var match = sortable.resourcepattern[i].exec(document.location.href);
      if(match) {
        sortable.resource = match[1];
        break;
      }
    }
    table.each(function() {
      var forecast = $(this).find('thead > tr > th.column-forecast');
      if(forecast.size()) {
        i18n.translate('Update', 'horae.planning', function(str) {
          var update = $('<a class="button button-discreet" href="javascript://">'+str+'</a>').click(sortable.update_forecast);
          forecast.append(update);
        });
        sortable.forecast = forecast.index();
      }
      $(this).find('tbody > tr').each(function() {
        var id = parseInt($(this).find('td:nth-child(2) a').html());
        sortable.ids.push(id);
        $(this).attr('id', 'ticket'+id);
        $(this).data('url', $(this).find('td:nth-child(2) a').attr('href')+'/plan.helper');
        var td = $(this).find('td:first');
        td.find('div').remove();
        var handle = $('<a class="button button-discreet handle">░</a>').css('cursor', 'move').mousedown(sortable.start).mouseup(sortable.stop);
        td.append(handle);
      });
      $(this).sortable({
        items: 'tbody > tr:not(.disabled)',
        handle: '.handle',
        update: sortable.update,
        placeholder: 'ui-state-highlight',
        forcePlaceholderSize: true
      });
    });
  }
  
  sortable.start = function(event) {
    var item = $(this).closest('tr');
    var next = item.next('tr');
    var prev = item.prev('tr');
    item.data('next', next ? next.attr('id') : false);
    item.data('prev', prev ? prev.attr('id') : false);
    $.ajax({
      async: false,
      url: item.data('url'),
      data: {
        action: 'disabled'
      },
      success: $.proxy(function(data) {
        if(!data)
          return
        this.find('#ticket'+data.join(', #ticket')).addClass('disabled').css('opacity', '0.5');
        this.sortable('option', 'items', 'tbody > tr:not(.disabled)');
      }, item.closest('table')),
      dataType: 'json',
      method: 'get'
    });
  }
  
  sortable.update = function(event, ui) {
    sortable.item = $(ui.item);
    var prev = sortable.item.data('prev');
    var next = sortable.item.data('next');
    sortable.action = false;
    sortable.position = false;
    if(next && sortable.item.prevAll('#'+next).size()) {
      sortable.action = 'movedown';
      sortable.position = sortable.item.prev('tr').attr('id').substr(6);
    }
    if(!sortable.action && prev && sortable.item.nextAll('#'+prev).size()) {
      sortable.action = 'moveup';
      sortable.position = sortable.item.next('tr').attr('id').substr(6);
    }
    if(!sortable.action)
      return;
    dialogs.show_loading('Updating order...', 'horae.planning');
    params = {'action': sortable.action, 'position': sortable.position};
    if(sortable.resource !== false)
      params['resource'] = sortable.resource;
    $.ajax({
      url: sortable.item.data('url'),
      data: params,
      success: function(data) {
        dialogs.hide_loading()
      },
      dataType: 'JSON',
      method: 'GET',
      error: function() {
        dialogs.hide_loading();
      }
    });
  }
  
  sortable.update_forecast = function(event) {
    dialogs.show_loading('Updating forecast...', 'horae.planning');
    params = {'action': 'info', 'ids': sortable.ids.join(',')};
    if(sortable.resource !== false)
      params['resource'] = sortable.resource;
    $.ajax({
      url: $(this).closest('table').find('tbody tr:first').data('url'),
      data: params,
      success: function(data) {
        if(!data) {
          dialogs.hide_loading();
          return;
        }
        for(var i=0; i<data.length; i++) {
          var item = data[i];
          $('#ticket'+item.id+' td:eq('+sortable.forecast+')').html(item.forecast);
        }
        dialogs.hide_loading();
      },
      dataType: 'JSON',
      method: 'GET',
      error: function() {
        dialogs.hide_loading();
      }
    });
  }
  
  sortable.stop = function(e) {
    $(this).closest('tbody').find('tr').removeClass('disabled').css('opacity', '1');
  }
  
  initialization.register(sortable.init);
  
})(jQuery);
