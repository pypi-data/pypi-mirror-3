function TabClicked(event,ui){
    var ksk = 0.05 ;
    var taw = 0;
    var txnr= true;
    var ts;
    var div = $(ui.panel);
    if (div.parent().data('TA2width')) {
      ts = $('textarea',div);
      ts.each(function(){
        var t = $(this);
        var tt = t.parent().width();
        tt = tt - tt * ksk ;
        if (((taw > 0) && (taw < tt)) || (taw == 0)) {
          taw = tt ;
        }
      });
      ts.each(function(){
        var t = $(this);
        t.width(taw);
      });
      if (div.parent().data('TX2width')) {
        txnr = false;
        $('input[type="text"]',div).each(function(){
          var x = 0;
          var t = $(this);
          if (taw > 0) {
            x = taw ;
            t.width(taw);
          } else {
            x = t.parent().width();
            x = x - x * ksk ;
            t.width(x);
          }
        });
      }
    }
    if (txnr && (div.parent().data('TX2width'))) {
      $('input[type="text"]',div).each(function(){
          var x = 0;
          var t = $(this);
          x = t.parent().width();
          x = x - x * ksk ;
          t.width(x);
      });
    }
    // Height
    var HH = div.parent().data('TA2height');
    if (HH < 0) {
      var ss = div.data('TAheight');
      ts = $('textarea:visible',div);
      if (ts.length == 1) {
          if (ss > 0) {
              ts.height(ss);
          } else {
              var x = 0 ;
              if (div.data('ManualInsert') == true) {
                    x = ts.parent().parent().height();
                    ts.height(x);
              } else {
                    x = ts.parent().parent().parent().parent().parent().height();
                    x = x - 0.1 * x ;
                    ts.height(x);
              }
              div.data('TAheight',x);
          }
      }  
    } else if (HH > 0){
      ts = $('textarea',div);
      ts.each(function(){
        $(this).height(HH);
      });
    }
}

function BeAccordion(id) {
      $('#'+id).accordion();
}
function BeTab(id) {
    $(id).tabs({
        show: TabClicked,
        cookie: {
            name: 'adm_inlines2tabs',
            expires: 7,
            path: '/'
        }
    });

}

function ManualTabInsert(insert,TH,TC) {
    var tabs = 0 ;
    if (insert && insert.length > 0) {
        for (var i in insert) {
            var s = insert[i];
            var t = $(s.move);
            if (t.length > 0) {
                TH.append('<li><a href="#'+s.id+'">'+s.name+'</a></li>');
                t.clone(true).attr('id',s.id).addClass('tabbody').appendTo(TC);
                t.remove();
                tabs += 1;
                $('#'+s.id,TC).data('ManualInsert',true);
            }
        }
    }
    return tabs;
}

function Inlines2Tabs(insert) {
    $('div.form-row a.add-another').remove();
    $('input[name=_addanother]').remove();
    $('div.inline-group:first').before('<div id="tab_container"></div>');
    var TC = $('#tab_container');
    //TC.append('<ul id="tabs"></ul>');
    //var TH = $('#tabs',TC);
    TC.append('<ul></ul>');
    var TH = $('ul',TC);
    // create tabs
    var tabs = 0 ;
    tabs += ManualTabInsert(insert.before,TH,TC);
    $('div.inline-group').each(function() {
      var t = $(this);
      tabs += 1;
      var tid = t.attr('id');
      var h = $('h2:first',t).text();
      $('h2:first',t).remove();
      TH.append('<li><a href="#'+tid+'">'+h+'</a></li>');
      t.clone(true).addClass('tabbody').appendTo(TC);
      t.remove();
    });
    tabs += ManualTabInsert(insert.after,TH,TC);
    TC.data('count',tabs);
    if (TC.data('count') > 0) {
      TC.data('TA2width',true);
      TC.data('TX2width',true);
      TC.data('TA2height',0);
      if (insert.TA2height != 0){ TC.data('TA2height',insert.TA2height); }
      if (insert.TA2width == false) { TC.data('TA2width',false); }
      if (insert.TX2width == false) { TC.data('TX2width',false); }
      if (insert.MinHeight > 0) {
          $('div.tabbody', TC).css('min-height',insert.MinHeight);
      }
      BeTab(TC);
    }
}
function AsvAdminInitSortable(SID,url) {
    if (SID[0] != '#') {
        SID = '#' + SID;
    }
    $(SID).sortable({
        items: 'div.sortable',
        start: function(event, ui) {
                    $('img',ui.item).toggle();
                    $(ui.item).css('opacity',50);
        },
        stop: function(event, ui) {
                    $('img',ui.item).toggle();
                    $(ui.item).css('opacity',100);
        },
        update: function(event, ui) {
                    var a = $(SID).sortable('toArray');
                    var m = $('input.asv__model_mark',SID).val();
                    var ee = {
                        'mark': m,
                        'order': a
                    };
                    ee = $.toJSON(ee);
                    $.post(url, {
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                        reorder: ee
                    }, function(data, textStatus, jqXHR) {
                        //alert(textStatus);
                    }, 'json');
        },
        opacity: 0.6,
        placeholder: "ui-state-highlight"
    });
}
;
