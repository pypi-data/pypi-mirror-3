(function( $ ){

    $.fn.entitymd = {};  // namespace

    $.fn.entitymd.get_metadata = function() {
        var title = $(this).attr('title');
        $.get($(this).attr('href'), function(data) {
            $('div#metadata-contents').html(data).dialog({
                width: 800,
                height: 400,
                title: title,
                buttons: {
                    'Close': function() { $(this).dialog("close"); }
                }
            });
        });
        return false;
    };
    
    $.extend($.ui.dialog.defaults, {
        overlay : {opacity: 1.0},
        modal: true
    });

})( jQuery );
