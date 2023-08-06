
cocktail.bind(".OrderContentView", function ($contentView) {

    if ($contentView.find(".Table tbody tr").length > 1) {

        var th = document.createElement('th');
        $contentView.find(".Table thead tr").prepend(th);
        
        $contentView.find(".Table tbody tr")
            .hover(
                function() { jQuery(this.cells[0]).addClass('showDragHandle'); },
                function() { jQuery(this.cells[0]).removeClass('showDragHandle'); }
            )          
            .each(function (i) {
                var td = document.createElement('td');
                td.className = 'dragHandle';
                jQuery(this).prepend(td);
                jQuery(this).attr('id', jQuery(this).find(":checkbox").val());
            });

        function renderEvenOdd() {
            $contentView.find(".Table tbody tr").each(function (i) {
                jQuery(this).removeClass();
                if (i % 2) {
                    jQuery(this).addClass("odd");
                }
                else {
                    jQuery(this).addClass("even");
                }
            });
        }
  
        var member = jQuery(this).closest(".BackOfficeCollectionView").get(0).member;
        var edit_stack = jQuery(this).closest(".BackOfficeItemView").get(0).edit_stack;
     
        $contentView
            .append("<div class=\"error\" style=\"display:none;\"></div>")
            .find(".Table").tableDnD({
                onDrop: function(table, row) {
                    
                    renderEvenOdd();                
                    
                    var position = jQuery(table).find("tbody tr").index(row);
                    var url = '/' + cocktail.getLanguage() + cms_uri + '/order?';
                    url += "selection=" + jQuery(row).attr('id') + "&";
                    url += "member=" + member + "&";
                    url += "edit_stack=" + edit_stack + "&";
                    url += "action=order&";
                    url += "format=json&";
                    url += "position=" + position;
                    
                    if (table.entrySelector) {
                        table._entries = jQuery(table).find(table.entrySelector);
                    }

                    jQuery.ajax({
                        url: url,
                        type: "GET",
                        data: {},
                        dataType: "json",
                        contentType: "application/json; charset=utf-8",
                        success: function(json){
                            jQuery(".error").hide();
                            if (json.error) {
                                jQuery(".error").html(json.error).show("slow");
                            }
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            jQuery(".error")
                                .hide()
                                .html(textStatus).show("slow");
                        }
                    });        		        		
                                    
                },
                dragHandle: "dragHandle",
                onDragClass: "mydragClass"
            });
    }
});

