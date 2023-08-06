    /*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".UserForm", function ($form) {

    function togglePasswords() {
                
        var $passwordField = $form.find(".password_field");
        var $passwordConfirmationField = $form.find(".password_confirmation_field");
        
        $passwordField.find(".control").val("");
        $passwordConfirmationField.find(".control").val("");

        if (this.checked) {
            $passwordField.show();
            $passwordConfirmationField.show();
        }
        else {
            $passwordField.hide();
            $passwordConfirmationField.hide();
        }
    }

    $form.find(".change_password_field .control")
        .each(togglePasswords)
        .click(togglePasswords)
        .change(togglePasswords);
});

