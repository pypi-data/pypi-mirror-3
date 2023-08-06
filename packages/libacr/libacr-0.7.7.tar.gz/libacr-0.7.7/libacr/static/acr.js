
function acr_delete_slice(delete_slice_path, slice_id)
{
    btn = "#edit_slice_"+slice_id;

    if (confirm('Really delete slice?')) {
        del_uri = delete_slice_path+'/'+slice_id;
        jQuery.get(del_uri, function() {window.location.reload(true);});
    }
}

function acr_move_slice(move_slice_path, slice_id, value)
{
    move_uri = move_slice_path+'/'+slice_id+'?value='+value;
    jQuery.get(move_uri, function() {window.location.reload(true);});
}

function acr_show_slice_bar(slice, enabled)
{
    slicebar = jQuery(slice).find('.acr_edit_button');
    if (enabled) {
        slicebar.css('z-index', 999);
        slicebar.css('opacity', 1);
    } else {
        slicebar.css('z-index', 0);
        slicebar.css('opacity', 0.3);
    }
}

function acr_show_menu(where)
{
    menu = jQuery(where).parent().children('ul');
    menu.toggle();
    return false;
}
