(function($) {
  
  $(document).ready(function() {
    
    // Table configlet
    var counter = 1;
    var title = false;
    
    var onLoad = function(){
      var overlay = this.getOverlay();
      var container = overlay.find('div>div');
      var maxheight = $(window).height() - parseInt(overlay.css('top')) * 2;
      container.css('max-height', maxheight + 'px');
      container.css('overflow', 'auto');
      
    }
    
    $('.table-configlet .table-columns').each(function() {
      var cell = $(this).parent();
      var trigger = $('<a href="javascript://" rel="#columns_'+counter+'"><img src="++resource++table_icon.gif" /></a>');
      if(!title)
        title = cell.closest('table').find('thead > tr > th:eq(2)').html();
      var overlay = $('<div id="columns_'+(counter++)+'" class="overlay overlay-ajax" />');
      var content = $('<div><h2 class="documentFirstHeading">'+title+'</h2></div>');
      var save = $(this).closest('form').find('input.context:last').clone();
      save.click(function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        $(this).closest('td').find('a[rel]').data('overlay').close();
      });
      cell.append(overlay).append(trigger);
      content.append($(this));
      content.append(cell.find('p.discreet'));
      content.append(save);
      overlay.append(content.wrap('<div class="pb-ajax" />').parent()).hide();
      trigger.overlay({
        closeOnClick: false,
        closeOnEsc: false,
        onLoad: onLoad,
      });
    });
    
    // Columns edit form
    counter = 1;
    $('.table-columns tbody tr').each(function() {
      $(this).attr('id', 'column_'+(counter++));
      var handle = $('<td />')
        .mousedown(function(e) {
          e.preventDefault();
          ploneDnDReorder.table = $(this).closest('table');
          ploneDnDReorder.rows = $(this).closest('tbody').find('tr');
          $.proxy(ploneDnDReorder.doDown, this)(e);
        })
        .mouseup(function(e) {
          e.preventDefault();
          var _temp = ploneDnDReorder.updatePositionOnServer;
          ploneDnDReorder.updatePositionOnServer = function() {};
          $.proxy(ploneDnDReorder.doUp, this)(e);
          ploneDnDReorder.updatePositionOnServer = _temp;
        })
        .addClass("draggingHook")
        .addClass("draggable")
        .css("cursor","ns-resize")
        .html('&#x28ff;');
      $(this).prepend(handle);
    });
    $('.table-columns thead tr').prepend('<th class="nosort" />');
    $('.table-columns tfoot tr td').attr('colspan', $('.table-columns tfoot tr td').attr('colspan')+1);
    $('input[name$="_add_column"][type="submit"]').click(function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      var row = $(this).closest('table').find('tbody > tr:last').clone(true);
      row.attr('id', row.attr('id').replace('column_', '')+1);
      row.find('input:text').val('');
      row.find('input:checkbox').attr('checked', '');
      row.find('option').attr('selected', '');
      $(this).closest('table').find('tbody').append(row);
    });
    
    // Table edit view
    $('table.table td.icon:not(.hidden)').each(function() {
      var format = $(this).parents('table').hasClass('gif') ? 'gif' : 'png';
      if(!$.trim($(this).html()))
        return;
      $(this).wrapInner('<span class="icon-content" />');
      $(this).prepend('<img class="trigger" src="info_icon.'+format+'" />');
      $(this).hover(function() {
        $(this).find('.icon-content').css($(this).find('.trigger').position()).fadeIn(200);
      },
      function() {
        $(this).find('.icon-content').fadeOut(200);
      });
    });
    $('table.table .add-row').each(function() {
      var format = $(this).parents('table').hasClass('gif') ? 'gif' : 'png';
      $(this).find('td:not(.hidden) input:not([type=submit]), td:not(.hidden) textarea').each(function() {
        $(this).wrap('<span class="wrap" />');
        $(this).parent().width(30).height($(this).outerHeight()).css('overflow', 'hidden');
        $(this).css($(this).position());
      })
      .focus(function() {
        $(this).parent().css({
          'overflow': 'visible',
          'z-index': 1
        });
      }).
      blur(function() {
        $(this).parent().css({
          'overflow': 'hidden',
          'z-index': 0
        });
      });
      $(this).find('td:not(.hidden) textarea').css('width', 150);
      $(this).find('.context').before('<a href="javascript://" class="icon add"><img src="add_icon.'+format+'" /></a>');
      $(this).find('.add').click(function(event) {
        event.preventDefault();
        var row = $(this).parents('.add-row');
        var new_row = row.clone(true);
        row.after(new_row);
        row.find('.add').after('<a href="javascript://" class="icon delete"><img src="delete_icon.'+format+'" /></a>');
        row.find('.delete').click(function(event) {
          event.preventDefault();
          $(this).parents('.add-row').remove();
        });
        row.find('.context, .add, input[name$=".row.position"]').remove();
        new_row.find('input:first').focus();
      });
    });
    var rows = $('table.table .manage, table.table thead th:last');
    if(rows.size() > 1) {
      rows.each(function() {
        var format = $(this).closest('table').hasClass('gif') ? 'gif' : 'png';
        $('<a href="javascript://" class="icon add"><img src="add_icon.'+format+'" /></a>').appendTo($(this))
        .click(function(event) {
          event.preventDefault();
          var row = $(this).closest('tr');
          var table = row.closest('table');
          var top = row.parent('thead').size() > 0;
          table.find('.add-row').each(function() {
            if(!top) {
              $(this).data('current', true);
              var next = row;
              while(next.size() > 0) {
                var possible = next.next('tr.add-row');
                if(possible.size() == 0 || possible.data('current'))
                  break;
                next = possible;
              }
              $(this).insertAfter(next);
              $(this).data('current', false);
            } else
              $(this).insertBefore(table.find('tbody tr:not(.add-row)').get(0));
          });
          var position = table.find('.add-row:has(.context)').index();
          var name = table.find('tr.add-row .context').attr('name').replace('add', 'position');
          if(table.find('input[name="'+name+'"]').size() > 0)
            table.find('input[name="'+name+'"]').val(position);
          else
            table.find('tr.add-row .context').before('<input type="hidden" name="'+name+'" value="'+position+'" />');
        });
      });
    }
    $('table.table td.hidden').each(function() {
      if(!$.trim($(this).html()))
        return;
      var format = $(this).parents('table').hasClass('gif') ? 'gif' : 'png';
      var hidden = $(this).parent().find('td:first').find('.hidden-content');
      if(!hidden.size()) {
        $(this).parent().find('td:first').prepend('<span class="hidden-content"><img class="trigger" src="search_icon.'+format+'" /><span class="content"><table></table></span></span>')
        hidden = $(this).parent().find('td:first').find('.hidden-content');
        hidden.hover(function() {
          $(this).find('.content').fadeIn(200).css('display', 'block');
        },
        function() {
          $(this).find('.content').fadeOut(200);
        });
      }
      hidden.find('table').append('<tr><th>'+$(this).parents('table').find('th.'+$(this).attr('class').match(/column-[^\s]+/)).html()+'</th><td>'+$(this).html()+'</td></tr>');
    }).remove();
    $('table.table th.hidden').remove();
  });
  
})(jQuery);
