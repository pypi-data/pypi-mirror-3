tinyMCE.init({
    mode: 'specific_textareas',
    editor_selector: 'mceEditor',

    plugins : 'advlink,inlinepopups,fullscreen,table,contextmenu',

    theme: 'advanced',
    theme_advanced_toolbar_location : 'top',
    theme_advanced_toolbar_align : 'left',
    theme_advanced_buttons1: "formatselect,styleselect,|,bold,italic,strikethrough,|,justifyleft,justifycenter,justifyright,|,bullist,numlist,table,indent,outdent,|,link,anchor,unlink,image,|,code,fullscreen",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",

    theme_advanced_blockformats: "p,h2,h3,blockquote,pre",

    content_css : $('link[rel="root"]').attr('href') + '/@@/asm.cmsui/tinymce_content.css',

    dialog_type : 'modal',

    file_browser_callback: 'asmcmsFileBrowser',

    style_formats: {
        teaserimage: {title: 'Teaser image', selector : 'img', classes : 'teaser'},
    },

    document_base_url: document.baseURI,

    width: "100%",
    height: 400,

    gecko_spellcheck : true
});

tinyMCE.init({
    mode: 'specific_textareas',
    editor_selector: 'mceEditorSmall',

    plugins : 'advlink,contextmenu',

    theme: 'advanced',
    theme_advanced_toolbar_location : 'top',
    theme_advanced_toolbar_align : 'left',
    theme_advanced_buttons1: "formatselect,styleselect,|,bold,italic,strikethrough,|,link,anchor,unlink,|,code",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",

    theme_advanced_blockformats: "p",

    content_css : $('link[rel="root"]').attr('href') + '/@@/asm.cmsui/tinymce_content.css',

    dialog_type : 'modal',

    document_base_url: document.baseURI,

    width: "100%",
    height: 100,

    gecko_spellcheck : true
});


function asmcmsFileBrowser(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({
        url: $('base').attr('href') + '/@@tinymce-linkbrowser',
        width: 400,
        height :400,
        inline: "yes",
    }, {window: win,
        input: field_name}
    );
    return false;
}
