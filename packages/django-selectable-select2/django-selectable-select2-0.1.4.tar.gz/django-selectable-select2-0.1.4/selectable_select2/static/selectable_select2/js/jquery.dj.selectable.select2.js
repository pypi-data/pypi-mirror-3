(function($) {
  $(document).ready(function() {

    var djs2limit = 16;

    var $selectitems = $("[data-selectable-type]=select2");
    $selectitems.each( function(index) {
        var $selectitem = $(this);
        var djs2url = $selectitem.data('selectableUrl');

        $selectitem.select2({
            // minimumInputLength : 1,
            width            :  'resolve',
            minimumResultsForSearch: djs2limit,
            allowClear       :  true,
            ajax             :  {
                                  url : djs2url,
                                  dataType: 'json',
                                  data : function (term, page) {
                                       return { term : term, limit: djs2limit, page: page };
                                  },
                                  results : function (data, page) {
                                      var more = data.meta.next_page ? true : false;
                                      return { results : data.data, more : more };
                                  }
                                },
            initSelection    :  function (element, callback) {
                                  /** TODO: adjust this to work with multiple selection */
                                    var data = {};
                                    var el_val = element.val();
                                    var initial_selection = element.data('initialSelection');
                                    if (initial_selection) {
                                      data = {
                                        id : el_val,
                                        value : initial_selection
                                      };
                                    }

                                    callback(data);
                                },
            formatResult     :  function (state) {
              return state.label;
            },
            formatSelection  :  function (state) {
              return state.value;
            },
            doEscapeMarkup: false
        });
     });
  });
})(jQuery);
