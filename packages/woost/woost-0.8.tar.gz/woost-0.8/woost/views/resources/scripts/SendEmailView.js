/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".SendEmailView", function ($sendEmailView) {
    setTimeout("update_progress({0}, '{1}')".format(this.task_id, this.edit_stack), 3000);
});

function update_progress(task_id, edit_stack) {

    var url = "./send_email/mailing_state/" + task_id
    if (edit_stack)
        url += "?edit_stack=" + edit_stack

    jQuery.getJSON(url, function(data) {
        var progress = 0;

        if (!data) {
            jQuery(".mailing_info").html(jQuery("<div>").addClass("error_box").text(cocktail.translate("woost.extensions.mailer.SendEmailView error email delivery")));
        } else {

            if (!data.completed) {
                progress = parseInt(parseInt(data.sent) * 100 / parseInt(data.total));
                setTimeout("update_progress({0}, '{1}')".format(task_id, edit_stack), 3000);
            } else {
                progress = 100;
                jQuery(".mailing_info h3").text(cocktail.translate("woost.extensions.mailer.SendEmailView email delivery finished"));
                if (data.errors != 0) {
                    jQuery(".mailing_info").append(jQuery("<div>").addClass("error_box").text(cocktail.translate("woost.extensions.mailer.SendEmailView error email delivery")));
                }
            }

            jQuery(".mailing_info .progress").css("width", progress + "%");
            jQuery(".mailing_info .progress-text").text(progress + "%");
            jQuery(".mailing_info .summary").html(cocktail.translate("woost.extensions.mailer.SendEmailView mailer summary").format(parseInt(data.sent), parseInt(data.total)));
        }
    });
}

String.prototype.format = function(){
    var pattern = /\{\d+\}/g;
    var args = arguments;
    return this.replace(pattern, function(capture){ return args[capture.match(/\d+/)]; });
}
