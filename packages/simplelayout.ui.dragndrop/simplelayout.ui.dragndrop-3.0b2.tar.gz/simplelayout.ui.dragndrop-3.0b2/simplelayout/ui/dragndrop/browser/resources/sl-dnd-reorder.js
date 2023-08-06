var ui_dragging = false;

function setHeightOfEmptyDropZone(){
    //set height of empty dropzones
    var sl_slots = jq('.simplelayout-content [id*=slot]');
    var heightest_slot = 0;

    if (sl_slots.length > 1){
        sl_slots.each(function(i,o){
            var $obj = jq(o);
            //get height
            if ($obj.height() > heightest_slot){
                heightest_slot = $obj.height();
            }

            var $items = $obj.contents('.BlockOverallWrapper');
            if ($items.length == 0){
                if (!$obj.hasClass('emptyZone')){$obj.addClass('emptyZone')};
            }else{
                $obj.removeClass('emptyZone');
            }
        });

        //set height on empty slots
        //reset
        sl_slots.css('height','');
        var $emptySlots = jq('.emptyZone');
        if (heightest_slot == 0){$emptySlots.css('height','300px')};
        if (heightest_slot != 0){$emptySlots.css('height',heightest_slot+'px')};
    }
}

function refreshSimplelayoutDragndropOrdering() {

    var sl_content = jq('.simplelayout-content');
    var slots = jq('.simplelayout-content [id*=slot]');

    jq('.simplelayout-content [id*=slot]').sortable({
		items: '.BlockOverallWrapper',
        handle: jq('.BlockOverallWrapper .sl-controls .document-action-dragme'),
        scroll : true,
		forcePlaceholderSize : false,
		placeholder: 'placeholder',
        connectWith: jq('.simplelayout-content [id*=slot]'),
        /* appendTo : '.BlockOverallWrapper',*/
		opacity: 0.5,
		tolerance:'pointer',
		start: function(e,ui) {
            ui_dragging = true;
            ui.placeholder.css("width", ui.item.width()-1);
            ui.placeholder.css("height", ui.item.height()-1);
            simplelayout.toggleEditMode(enable=false, ui.item.find('.sl-controls'));
            slots.addClass('highlightBorder');

		},
		update: function(e, ui){
            var ids = new Array();
            jq('.BlockOverallWrapper').each(function(i, o) { ids.push(o.id); });
            ids = ids.join(',');
            var slot = jq(e.target).attr('id');
            var column = jq(e.target).attr('class');

            var obj_uid = jq(ui.item[0]).attr('id');
            var activeLayout = jq('.sl-layout.active',ui.item);


            //jq.post('sl_dnd_saveorder', { uids : ids ,slot:slot,column:column,obj_uid:obj_uid});
            //refresh paragraph after reordering
            ajaxManager.add({url:'sl_dnd_saveorder',
                            type:'POST',
                            data:{ uids : ids ,slot:slot,column:column,obj_uid:obj_uid},
                            success:function(){
                                if (activeLayout.length != 0){
                                    simplelayout.refreshParagraph(activeLayout[0]);
                                    }
                                }
                            });

		},
        /*change: function(e, ui){
            setHeightOfEmptyDropZone();

		}, */
		stop: function(e, ui){
            ui.item.removeAttr("style");
            simplelayout.toggleEditMode(enable=true, ui.item.find('.sl-controls'));
            setHeightOfEmptyDropZone();
            slots.removeClass('highlightBorder');
            jq(".simplelayout-content").trigger('afterReorder');

		}

    })

    sl_content.bind("toggleeditmode", function(e){
        sl_content.sortable('enable');
    });

    setHeightOfEmptyDropZone();

}

jq(refreshSimplelayoutDragndropOrdering);
