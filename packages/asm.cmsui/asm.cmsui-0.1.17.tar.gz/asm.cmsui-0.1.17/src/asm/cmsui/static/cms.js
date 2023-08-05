var KEY_ESCAPE = 27;

$(document).ready(function(){
    // Showing/hiding navigation screen
    $(document).keydown(function(e) {
        if (e.which == KEY_ESCAPE) {
            toggle_navigation();
        }});

    $(".toggle-navigation").click(function() {toggle_navigation();});

    $("input.clear-first-focus").one('click', clear_input);

    $(".open-preview").click(show_preview);
    window.preview_location = $('link[rel="preview"]').attr('href');
    window.root = $('link[rel="root"]').attr('href');

    $("#navigation-tree")
    .bind("loaded.jstree", tree_select_current_node)
    .bind("dblclick.jstree", tree_open_selected_page)
    .bind("deselect_node.jstree select_node.jstree", tree_update_rename_icons)
    // TODO when we have icon from hovering and try to add onclick event to it,
    // it fires at some times. Try to find out why and enable this after that.
    // .bind("hover_node.jstree", tree_show_hover_icon)
    .bind("rename_node.jstree", tree_execute_rename_action)
    .bind("deselect_node.jstree select_node.jstree", tree_disable_delete_on_root_select)
    .bind("move_node.jstree", tree_move_selected_pages)
    .jstree({
        plugins: [ "themes", "xml_data", "ui", "types", "dnd", "crrm"],
        xml_data: {
            ajax: {
                url: $('#navigation-tree a').attr('href'),
                data: function(node) {
                    if (node.attr) {
                        return {parent_id: node.attr("id")};
                    }
                    // We are opening navigation for the first time on current
                    // page => there is no parent as we want to get the root
                    // of the navigation tree. We also want to get all the
                    // branches from current page to the root.
                    return {page_id: current_page_id()};
                }
            }
        },
        core: {
            animation: 0
        },
        ui: {
            theme_name: 'classic'
        },
        types: {
            types: {
                htmlpage: { icon:  { image: root+'/@@/asm.cmsui/icons/page_white.png'}},
                homepage: { icon:  { image: root+'/@@/asm.cmsui/icons/house.png'}},
                news: { icon:  { image: root+'/@@/asm.cmsui/icons/newspaper.png'}},
                sponsorsarea: { icon:  { image: root+'/@@/asm.cmsui/icons/page_white_medal.png'}},
                asset: { icon:  { image: root+'/@@/asm.cmsui/icons/page_white_picture.png'}},
                programsection: { icon:  { image: root+'/@@/asm.cmsui/icons/film.png'}},
                redirect: { icon:  { image: root+'/@@/asm.cmsui/icons/link_go.png'}},
            }
        },
        crrm: { move: { check_move: tree_check_move_not_outside_root } }
    });

    $('.expandable .opener').click(toggle_extended_options);

    $('.url-action').click(trigger_url_action);
    $('form[id="addpage"]').submit(add_page);

    $('#delete-page').click(delete_page);

    $('.expandable .error').each(expand_section);

    if (window.location.hash == "#show-navigation") {
        show_navigation();
    }
});

function tree_check_move_not_outside_root(move) {
    var root_nodes = this._get_children(-1);
    var type = move.p;
    if ($.inArray(type, ["before", "after"]) != -1 &&
        arrays_intersect(move.r, root_nodes)) {
        return false;
    }
    return true;
}

function tree_update_rename_icons(event, data) {
    var tree = data.inst;
    $("#navigation-tree").find(".rename-page").each(function() {
        var node = $(this).parent();
        if (!tree.is_selected(node)) {
            tree_hide_rename_icon(tree, node);
        }
    });
    $(tree.get_selected()).each(function() {
        tree_show_rename_icon(tree, this);
    });
}

function tree_show_hover_icon(event, data) {
    var tree = data.inst;
    var node = data.rslt.obj;
    tree_update_rename_icons(event, data);
    tree_show_rename_icon(tree, node);
}

function tree_rename_node(rename_anchor) {
    var tree = $.jstree._reference('#navigation-tree');
    var node_id = $(rename_anchor).attr("href");
    var node = tree._get_node(node_id);
    tree.set_text(node, $(node).children("a").first().attr('page_name'));
    tree.rename(node);
}

function tree_execute_rename_action(event, data) {
    var new_name = data.rslt.name;
    var node = data.rslt.obj;
    var tree = data.inst;
    tree.set_text(node, "Updating...");
    $(node).children("a").addClass("jstree-loading");
    $.post(node_view(node, "rename"),
           {new_name: new_name, open_page_id: current_page_id()},
           function (data) {
               var result = JSON.parse(data);
               var tree = $.jstree._reference('#navigation-tree');
               $(node).children("a").removeClass("jstree-loading");
               tree.refresh();
               toggle_navigation = function() {
                   window.location = result['open_page'];
               }
           });
    return true;
}

function tree_show_rename_icon(tree, node) {
    // Do not show icons for root nodes.
    if (is_root_node(tree, node)) {
        return true;
    }
    var renamed = $(node).children(".rename-page");
    if (renamed.length == 0) {
        var id = $(node).attr("id");
        var name = $(node).children("a").first().attr('page_name')
        var rename_node = "<span class='rename-label'>("+name+")</span><a class='rename-page' href='#" + id + "' onclick='tree_rename_node(this)' title='Rename the page name that is visible in URLs.'>&nbsp;</a>";
        var links = $(node).find("a");
        var anchor = links.first().after(rename_node);
    }
    return true;
}

function tree_hide_rename_icon(tree, node) {
    if (!tree.is_selected(node)) {
        $(node).find(".rename-page").remove();
        $(node).find(".rename-label").remove();
    }
}

function tree_disable_delete_on_root_select(event, data) {
    var tree = data.inst;
    var target_nodes = tree.get_selected();
    var root_nodes = tree._get_children(-1);

    var delete_button = $('#delete-page');
    if (arrays_intersect(target_nodes, root_nodes)) {
        delete_button.attr('disabled', 'disabled');
    } else {
        delete_button.removeAttr('disabled');
    }
}

function current_page_id() {
    return $('link[rel="pageid"]').attr('href');
}

function application_view(view) {
    return $('link[rel="root"]').attr('href') + "/@@" + view;
}

function node_view(node, view) {
    return $('a', node).attr('href') + "/../@@" + view;

}

function is_root_node(tree, node) {
    return $.inArray(node, tree._get_children(-1)) != -1;
}

function tree_select_current_node(event, data) {
    // Show currently open page and its sub pages in navigation tree.
    var tree = data.inst;
    var opened_page_id = current_page_id();
    var node = tree._get_node("#" + opened_page_id)[0];

    tree.open_node(node);
    tree.select_node(node);
    // We don't know why we have to call save_selected here, but if we
    // don't then the selection disappears again. :/
    tree.save_selected();
    return true;
}

function tree_open_selected_page(event) {
    var node = event.target;
    // This check is here as if we double click iconed items, we'll get a
    // target that points to the actual icon. It does not have have any
    // URL information, but the parent node that holds the icon has.
    if (node.href == undefined) {
        node = node.parentNode;
    }
    if (node.href != undefined) {
        window.location = node.href + '/@@edit';
    }

    return true;
}

function tree_move_selected_pages(event, data) {
    var tree = data.inst;
    var type = data.rslt.p;
    var moved_nodes = data.rslt.o;
    var target_node = data.rslt.r;

    var ids = $(moved_nodes).map(function() { return $(this).attr('id'); }).get();

    $.post(node_view(target_node, 'arrange'),
           {ids: ids.join(","),
            type: type},
           function() { tree.refresh(); }
          );
}

function arrays_intersect(first, second) {
    for (id in first) {
        var obj = first[id];
        if ($.inArray(obj, second) != -1) {
            return true;
        }
    }
    return false;
}

function delete_page() {
    var tree = $.jstree._reference('#navigation-tree');
    var target_nodes = tree.get_selected();
    var self = this;

    // TODO if branch is closed, then deletion does not show its children.
    // but if it's open, then childrens' names are show in target.text().
    $('#confirm-deletion').dialog({
        resizable: false,
        height: 200,
        modal: true,
        buttons: {
            "Delete": function() {
                var target_ids = $(target_nodes).map(function() { return $(this).attr('id'); }).get();
                $.post(
                    application_view('delete'),
                    {ids: target_ids.join(","), current_page_id: current_page_id()},
                    handle_page_deletion
                );
                $(this).dialog("close");
            },
            "Cancel": function() {
                $(this).dialog("close");
            }}});
    return false;
}

function handle_page_deletion(data) {
    var result = JSON.parse(data);
    var tree = $.jstree._reference('#navigation-tree');
    if (result['status'] == 'ok') {
        $(result['deleted']).each(function() { tree.remove("#" + this)});
        tree.deselect_all();
        if (result['is_current_page_deleted']) {
            toggle_navigation = function() {
                window.location = result['target'];
            };
        }
    } else {
        window.location = result['target'];
    }
}

function expand_section() {
    $(this).parents('.section').each(function() {
        $(this).find('.expand').slideDown();
        $(this).find('.open').show();
        $(this).find('.closed').hide();
    });
}

function add_page() {
    var title = $(this).find("input[name=title]");
    if ($.trim(title.attr('value')).length == 0) {
        // XXX For some reason title.addClass() does not work.
        title.css("background-color", "#FBE3E4");
        title.css("color", "#8a1f11");
        title.css("border-color", "#FBC2C4");
        return false;
    }
    var t = $.jstree._reference('#navigation-tree');
    var add_page_url = node_view(t.get_selected(), 'addpage');

    $(this).ajaxError(
        function() {
            // XXX For some reason title.addClass() does not work.
            title.css("background-color", "#FBE3E4");
            title.css("color", "#8a1f11");
            title.css("border-color", "#FBC2C4");
        });

    $.post(add_page_url, $(this).serialize(),
           function(data) { window.location = data; });
    return false;
}

function trigger_url_action() {
    window.location = $(this).attr('href');
}

function toggle_extended_options() {
    $(this).parents('.expandable').find('.expand').slideToggle();
    $(this).parent().find('.open').toggle();
    $(this).parent().find('.closed').toggle();
};

function clear_input() {
    $(this).val('');
};

function hide_navigation() {
    $("#navigation").hide();
    $("#navigation-actions").hide();
    $("#content").show();
    $("#actions").show();
    toggle_navigation = show_navigation;
    return false;
}

function show_navigation() {
    $("#navigation").show();
    $("#navigation-actions").show();
    $("#content").hide();
    $("#actions").hide();
    toggle_navigation = hide_navigation;
    return false;
}

toggle_navigation = show_navigation;

function show_preview() {
    w = window.open(application_view('preview-window'));
    return false;
};
