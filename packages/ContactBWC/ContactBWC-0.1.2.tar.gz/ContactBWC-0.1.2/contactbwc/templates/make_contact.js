$(document).ready(function() {
    $('div#send-form-attachment_link > a').click(function () {
        add_attachment();
    });
});

function add_attachment() {
    var add_link = $('div#send-form-attachment_link-row');
    var form_code = '<div class="row odd">'+
        '        <div class="field-wrapper no-label">'+
        '            <input class="text" name="attachment" type="file" />'+
        '            <a class="remove_link" href="javascript:;">remove</a>'+
        '        </div>'+
        '</div>';
    $(add_link).before(form_code);
    fix_styles();
    $('a.remove_link').click( function() {
        $(this).parent().parent().remove();
        fix_styles();
    });
}

function fix_styles() {
    var add_link = $('div#send-form-attachment_link-row');
    $(add_link).parent().children('div').removeClass('odd');
    $(add_link).parent().children('div').removeClass('even');
    $(add_link).parent().children('div').removeClass('first');
    $('#send-form div:eq(1)').addClass('first');
    $(add_link).parent().children('div:odd').addClass('odd');
    $(add_link).parent().children('div:even').addClass('even');
}
