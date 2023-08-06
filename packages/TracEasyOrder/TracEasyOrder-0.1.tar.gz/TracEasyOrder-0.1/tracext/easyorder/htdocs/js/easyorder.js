$(document).ready(function() {
    $("table.listing").has("th:contains(Order)").each(function (idx) {
        // Hide the Order column in the table; there is probably a more
        // efficient way to be found to do this, but this will do for now
        var tableId = $(this).attr("id");
        $(this).children().children().each(function (idx) {
            // Every row has to have a unique ID for tableDnD to work correctly
            $(this).attr("id", tableId + "." + idx);
            $(this).children().last().hide();
        });

        // Enable drag-n-drop
        $(this).tableDnD({
            onDrop: function(table, row) {
                // There are more clever ways to do this somewhat more
                // efficiently, but for now it will suffice to update the order
                // values of all rows
                var href = document.location.pathname;
                if (href.match(/\/admin\/ticket\/customfields$/)) {
                    // Dumb special case for the Custom Field Admin plugin,
                    // which starts ordering from 0
                    var selector = "select[name^=order_]";
                    var offset = 0;
                } else {
                    var selector = "select[name^=value_]";
                    var offset = 1;
                }

                $(table).find(selector).each(function (idx) {
                    $(this).val(idx + offset);
                });
            }
        });
    });
});
