jQuery.extend(cw.cubes, {
    openidrelay: new Namespace('openidrelay')
});

jQuery.extend(cw.cubes.openidrelay, {
    fillLogFormAndPost: function(formid, inputid, openiduri) {
        $('#' + inputid).val(openiduri);
        $('#' + formid).submit();
    }
});


