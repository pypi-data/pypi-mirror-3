(function($) {
    $(function () {

        // Get the table list and checkboxes
        var table = $('table#listing-table');
        var checkboxes = table.find('input[type="checkbox"]');

        // Last checkbox is used for selecting multiple items with shift
        var lastcheckbox = undefined;
        var shiftkey = false;

        // On click store the shiftkey state since the change event doesn't
        // return keystates.
        checkboxes.click (function (e) {
            shiftkey = e.shiftKey;
        });

        // Event handler for checkbox value change
        checkboxes.change (function (e) {

            // Toggle selected class on current row
            if (this.checked) {
                $(this).parents("tr:first").addClass("selected");
            } else {
                $(this).parents("tr:first").removeClass("selected");
            }

            // Check if shiftkey is pressed and lastcheckbox is set
            if (shiftkey && lastcheckbox != undefined) {

                // Get checkboxes again since the order could have been changed
                checkboxes = table.find('input[type="checkbox"]');

                // Get the to be selected range
                var startindex = checkboxes.index(lastcheckbox);
                var endindex = checkboxes.index(this);
                if (startindex > endindex) {
                    var tempindex = endindex;
                    endindex = startindex;
                    startindex = tempindex;
                }

                // Select all the items in the range
                for (var i = startindex; i <= endindex; i++) {
                    $(checkboxes[i]).not(':checked')
                        .click()
                        .parents("tr:first").addClass("selected");
                }
            }

            // Store the last selected checkbox
            lastcheckbox = this;
        });

        // Select all the items on the current screen
        $('a#foldercontents-selectall').click (function (e) {

            // Check all the unchecked checkboxes
            checkboxes.not(':checked').click();

            // Call the change method manually
            // (the click event doesn't call this by itself)
            checkboxes.change();

            // Show table headers
            $('#all_items_on_page_selected').show();
            $('#all_items_in_folder_selected').hide();

            // Prevent href of the link to work
            return false;
        });

        // Select all the items in the current folder
        $('a#foldercontents-selectall-completebatch').click (function (e) {

            // Show table headers
            $('#all_items_on_page_selected').hide();
            $('#all_items_in_folder_selected').show();

            // Insert temp div which will contain the hidden inputs
            if ($('#temp_hidden_inputs').length == 0) {
                $('#folderlisting-main-table')
                    .prepend('<div id="temp_hidden_inputs"></div>');
            }

            // Get view url
            var view = "folder_contents_get_paths";
            var match = table.attr("class").match(/.*select_all-(\w+).*/);
            console.log(match);
            if (match != null) {
                view = match[1];
            }

            // Get the paths of all the items in the folder
            // excluding the specified list of paths (items of the current screen)
            $.post("folder_contents_get_paths",
                checkboxes.serialize(),
                function (data) {

                    // Add the paths as hidden inputs to the form
                    var paths = data.split('\n');
                    $('#temp_hidden_inputs').html('<input type="hidden" value="' + paths.join('" name="paths:list"/><input type="hidden" value="') + '" name="paths:list"/>');
                }
            );

            // Prevent href of the link to work
            return false;
        });

        // Deselect all items
        $('a#foldercontents-clearselection,#foldercontents-select-none').click (function (e) {

            // Check all the checked checkboxes
            checkboxes.filter(':checked').click();

            // Call the change method manually
            // (the click event doesn't call this by itself)
            checkboxes.change();

            // Show table headers
            $('#all_items_on_page_selected').hide();
            $('#all_items_in_folder_selected').hide();

            // Remove hidden inputs from the form
            $('#temp_hidden_inputs').remove();

            // Clear the last checked checkbox
            lastcheckbox = undefined;

            // Prevent href of the link to work
            return false;
        });
    })
})(jQuery);
