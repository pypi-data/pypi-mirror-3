jQuery(document).ready(function($) {
 /* search for fixed-feedback or fixed-alert, if it does not have a form in it,
    have it disappear in 30 seconds */
  $('div.fixed-feedback:not(:has(form)), div.fixed-alert:not(:has(form))').each(
    function(index, element) {
      var id = 'fixed-remove-button-'+index
      var thisel = $(element);
      thisel.children().first().before('<div style="float: right"><input type="button" id="'+id+'" class="hider" title="hide feedback" value="hide feedback" /></div>');
      $('#'+id).click(function(event) {
        thisel.slideUp('slow');
       }
      );
    }
  );
  
  /* add a feature to the SMI breadcrumb which displays the list of tabs
     for the next item below that item when the breadcrumb separator
     (a raquo) is clicked.  This list is retrieved from Silva when the sep.
     is clicked the first time*/
     
  var pathbar = $("div.pathbar").first();
  $("span.breadcrumb-sep", pathbar).each(function(index, element) {
    var jq_el = $(element);
    jq_el.click(function(event) {
      // if a tab is already open, hide it 
      var openItem = pathbar.data("tabListUl");
      var ex_list = jq_el.next('ul.smi-tab-list');
      // determine if the tab list is already present
      if (ex_list.length) {
        // if it is present, show/hide the list
        var ul = ex_list.first();
        if (openItem && (openItem.get(0) != ul.get(0))) {
          openItem.fadeOut();
          pathbar.removeData("tabListUl");
        }
        if (ul.css('display') == 'none') {
          ul.fadeIn();
          pathbar.data("tabListUl", ul);
        } else {
          ul.fadeOut();
          pathbar.removeData("tabListUl");
        }
      } else {
        if (openItem) {
          openItem.fadeOut();
          pathbar.removeData("tabListUl");
        }
        // the tab list is not present.  Retrieve it from Silva,
        // build the list, add it to the DOM and display it (using slide)
        var anchor = jq_el.siblings('a').first(),
            href = anchor.attr('href'),
            baseurl = href.replace(/\/edit\/.*$/, ''),
            url = href.replace(/\/edit\/.*$/,'/++rest++smitablist.get_tabs');
        // JSON call to get the list
        $.getJSON(url, function(data) {
          var od = element.ownerDocument,
              ul = od.createElement('ul'),
              ul = $(ul);
          ul.attr('class', 'smi-tab-list');
          ul.hide();
          // iterate over the items, building the list
          for (var item in data) {
            var tab = data[item],
                 action = baseurl + '/edit/' + tab[1];
            ul.append('<li><a href="'+action+'">'+tab[0]+'</a></li>');
          }
          // add completed list to DOM, animate the display, store the open item
          jq_el.after(ul);
          ul.fadeIn();
          pathbar.data("tabListUl", ul);
        });
      };
    });
  });
});