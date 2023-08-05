var graph = {
  
  ticks : false,
  plots : [],
  deadline : false,
  options: {
    bar: {
      seriesDefaults: {
        renderer: $.jqplot.BarRenderer,
        rendererOptions: {
          fillToZero: true,
          shadowDepth: 1,
          shadowOffset: 1,
          barWidth: 8,
          barMargin: 5,
          barPadding: 1
        }
      },
      axes: {
        xaxis: {
          renderer: $.jqplot.DateAxisRenderer,
          numberTicks: 25,
          tickRenderer: $.jqplot.CanvasAxisTickRenderer,
          tickOptions: {
            angle: -60,
            fontSize: '8pt'
          }
        },
        yaxis: {
          rendererOptions: {
            forceTickAt0: true
          },
          tickOptions: {
            formatString: '%.2f'
          }
        }
      },
      highlighter: {
        show: true,
        sizeAdjust: 10,
        showMarker: false,
        bringSeriesToFront: true
      },
      cursor: {
        show: true,
        zoom: true,
        looseZoom: true,
        showTooltip: false,
        constrainZoomTo: 'x',
        showVerticalLine: true,
        showHorizontalLine: true,
        followMouse: true
      },
      legend: {
        renderer: $.jqplot.EnhancedLegendRenderer,
        show: true,
        placement: 'outsideGrid',
        rendererOptions: {
          seriesToggle: true
        }
      },
      grid: {
        background: '#ffffff',
        borderColor: '#999999',
        borderWidth: 1.0
      }
    }
  }
  
};
(function($) {
  
  graph.init = function(container) {
    i18n.translate('Deadline', 'horae.planning', function(label) {
      graph.deadline = label;
      container.find('.planning-overview').each(function() {
        i18n.translate('Chart', 'horae.planning', $.proxy(function(label) {
          var index = $(this).find('tr.resource td.name:first').index();
          $(this).find('tr.resource, tr.milestone, tr.project').each(function() {
            var button = $('<a href="javascript://" class="button-graph button button-discreet button-alternative">'+label+'</a>');
            button.click(graph.show);
            $(this).find('td:eq('+(index-1)+')').append(button);
          });
        }, this));
      });
    });
  }
  
  graph.findnext = function(current, selector) {
    var next = current.next();
    while(next.size()) {
      if(next.is(selector))
        return next;
      next = next.next();
    }
    return false;
  }
  
  graph.findprev = function(current, selector) {
    var prev = current.prev();
    while(prev.size()) {
      if(prev.is(selector))
        return prev;
      prev = prev.prev();
    }
    return false;
  }
  
  graph.show = function() {
    if($(this).data('plot'))
      graph.plots[$(this).data('plot')].fadeIn();
    var row = $(this).closest('tr');
    if(graph.ticks == false) {
      graph.ticks = []
      row.closest('table').find('thead th.discreet.cw').each(function() {
        graph.ticks.push($(this).find('time').attr('date'));
      });
    }
    var data = [];
    var end = 0;
    var start = 10000000000;
    var series = [];
    var stopon = '.resource, .ticket';
    var nextquery = 'tr.execution, tr.resource, tr.ticket';
    var merge = false;
    var rows = row;
    if(row.hasClass('project') || row.hasClass('milestone')) {
      stopon = '.project, .milestone, .ticket';
      nextquery = 'tr.absence, tr.planned.current, tr.effective, tr.forecast.simple, tr.project, tr.milestone, tr.ticket';
      var id = row.find('td.name').prev('td').find('a').html().replace(/[^0-9]/g, '');
      if(row.hasClass('milestone') && !id)
        id = '0';
      rows = row.closest('tbody').find('tr.'+(row.hasClass('project') ? 'project' : 'milestone')+id);
      merge = true;
    }
    var deadline = row.find('td.deadline');
    if(deadline.size())
      deadline = deadline.index()-row.find('td.cw:first').index()+1;
    else
      deadline = false;
    var absi = [];
    var min = 0;
    var max = 0;
    var indexes = {};
    for(var r=0; r<rows.size(); r++) {
      var next = graph.findnext($(rows.get(r)), nextquery);
      while(next) {
        var s = [];
        var i = 0;
        var absence = next.hasClass('absence');
        var prev = 0;
        next.find('.cw').each(function() {
          val = parseFloat($(this).html());
          if(isNaN(val))
            val = 0;
          else if(absence)
            val = -val;
          else {
            start = Math.min(start, i);
            end = Math.max(end, i+1);
          }
          min = Math.min(val, min);
          max = Math.max(val, max);
          if(prev == 0 && val != 0 && i>0)
            s.push([graph.ticks[i-1], 0]);
          if(absence || prev != 0 || val != 0)
            s.push([graph.ticks[i], val]);
          prev = val;
          i++;
        });
        var done = false;
        if(merge) {
          if(absence)
            var name = graph.findprev(next, 'tr.resource').find('.name:first a').html();
          else
            var name = graph.findprev(next, 'tr.resource').find('.name:first a').html()+', '+graph.findprev(next, 'tr.resource').find('.name:last').html();
          var index = next.attr('class').replace(/[^a-zA-Z0-9]/g, '')+'___'+name.replace(/[^a-zA-Z0-9]/g, '');
          if(typeof indexes[index] == 'undefined')
            indexes[index] = data.length;
          else {
            if(!absence) {
              var serie = data[indexes[index]];
              var l = serie.length;
              var m = s.length;
              for(var n=0; n<m; n++) {
                var inserted = false;
                for(var i=0; i<l; i++) {
                  if(serie[i][0] == s[n][0]) {
                    serie[i][1] += s[n][1];
                    min = Math.min(min, serie[i][1]);
                    max = Math.max(max, serie[i][1]);
                    inserted = true;
                  }
                }
                if(!inserted)
                  serie.push(s[n]);
              }
            }
            done = true;
          }
        }
        if(!done) {
          if(absence)
            absi.push(data.length);
          data.push(s);
          series.push({
            label: next.find('td[colspan="4"]').html(),
            breakOnNull: true
          });
          if(merge)
            series[series.length-1].label = name+' ('+series[series.length-1].label.split(' ')[0]+')';
        }
        next = graph.findnext(next, nextquery);
        if(!next || next.is(stopon))
          break;
      }
    }
    for(var n=0; n<absi.length; n++) {
      data_reduced = data[absi[n]].slice(start, end);
      data[absi[n]] = [];
      prev = 0;
      for(var i=0; i<data_reduced.length; i++) {
        val = data_reduced[i][1];
        if(prev == 0 && val != 0 && i>0) {
          data[absi[n]].push(data_reduced[i-1]);
        }
        if(prev != 0 || val != 0) {
          data[absi[n]].push(data_reduced[i]);
        }
        prev = val;
      }
    }
    var d = 0;
    for(var n=0; n<absi.length; n++) {
      if(data[n-d].length)
        continue;
      data = data.slice(0, n-d).concat(data.slice(n-d+1));
      series = series.slice(0, n-d).concat(series.slice(n-d+1));
      d++;
    }
    $(this).data('plot', graph.plots.length);
    var plot = $('<div class="planning-plot"><div id="plot'+graph.plots.length+'" /></div>');
    $(this).closest('.planning-overview').append(plot);
    plot.find('div').css('height', $(window).height()-$(window).height()/5);
    plot.dialog({
      modal: true,
      draggable: false,
      resizable: false,
      minWidth: $(window).width()-100,
      show: 'fade',
      dialogClass: 'planning-plot-dialog'
    });
    options = $.extend(graph.options.bar, {});
    if(deadline) {
      deadline = graph.ticks[deadline];
      series.push({
        label: graph.deadline,
        xaxis: 'xaxis',
        color: '#663333',
        markerOptions: {
          show: false
        },
        renderer: $.jqplot.LineRenderer
      });
      data.push([[deadline, min*1.2], [deadline, max*1.2]]);
    }
    if(row.hasClass('resource'))
      var title = row.prevAll('tr.ticket').find('td.name').html()+': '+$(this).closest('td').next('td').html()+', '+$(this).closest('td').next('td').next('td').html();
    else
      var title = row.find('td.name').html();
    var options = $.extend(options, {
      title: title,
      series: series,
    });
    options.axes.xaxis.tickOptions.formatString = $.datepicker._defaults.dateFormat.replace('yy', '%y').replace('mm', '%m').replace('dd', '%d');
    console.log(data);
    console.log(series);
    var jqplot = $.jqplot('plot'+graph.plots.length, data, options);
    graph.plots.push(plot);
  }
  
  initialization.register(graph.init);
  
})(jQuery);
