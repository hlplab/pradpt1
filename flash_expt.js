function register(field, answer) {
    document.getElementById(field).value = answer;
    return true;
}

jQuery(document).ready(function(){
    jQuery('#content').hide();
    jQuery('input#consentcx').click(function(){
                if (jQuery(this).attr('checked') === true) {
                    jQuery('#instructions').hide();
                    jQuery('#content').show();
                    }
                }
            );
    var resultform = jQuery('#results');
    var trialcount = 68; //this is kind of a stab in the dark. I don't know how many trials to expect.
    for(var i=1;i<=trialcount;i++) {
        resultform.append('<input type="hidden" name="trial' + i + '" id="trial' + i + '" value="NA" /> ');
    }
});
