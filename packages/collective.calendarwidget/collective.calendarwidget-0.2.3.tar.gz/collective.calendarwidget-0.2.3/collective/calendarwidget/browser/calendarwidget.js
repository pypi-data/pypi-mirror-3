var $j = jQuery.noConflict();

$j(document).ready(function() {

    $j('input.calendarInput').datepicker({showButtonPanel: true});

    $j('input.calendarInput').each(function(f) {
            this.readonly = '1';
    });

})
