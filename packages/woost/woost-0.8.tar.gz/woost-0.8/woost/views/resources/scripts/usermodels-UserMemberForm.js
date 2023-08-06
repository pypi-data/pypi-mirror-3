/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2010
-----------------------------------------------------------------------------*/

(function () {
    
    function normalizeText(str){
        // Adapted from http://stackoverflow.com/questions/990904/javascript-remove-accents-in-strings
        var accented = 'ÀÁÂÃÄÅàáâãäåÒÓÔÕÕÖØòóôõöøÈÉÊËèéêëðÇçÐÌÍÎÏìíîïÙÚÛÜùúûüÑñŠšŸÿýŽž';
        var normalized = ['A','A','A','A','A','A','a','a','a','a','a','a','O','O','O','O','O','O','O','o','o','o','o','o','o','E','E','E','E','e','e','e','e','e','C','c','D','I','I','I','I','i','i','i','i','U','U','U','U','u','u','u','u','N','n','S','s','Y','y','y','Z','z'];
        return str.replace(new RegExp("[" + accented + "]", "g"), function (c) {
            var x = accented.indexOf(c);
            return x == -1 ? c : normalized[x];
        });
    }

    function memberNameFromLabel(label, isModel) {
        
        label = normalizeText(label);
        var parts = label.replace(/\W/g, " ").split(" ");
        
        if (isModel) {
            var name = "";
            for (var i = 0; i < parts.length; i++) {
                name += parts[i].charAt(0).toUpperCase();
                name += parts[i].substr(1);
            }
        }
        else {
            var name = parts.join("_").toLowerCase();
        }

        return name;
    }

    cocktail.bind(".UserMemberForm", function ($form) {

        var isModel = ($form.parents(".UserModel").length != 0);

        $form.find(".label_field input").blur(function () {
            if (this.value) {
                var nameBox = $form.find(".member_name_field input").get(0);
                if (!nameBox.value) {
                    nameBox.value = memberNameFromLabel(this.value, isModel);
                }
            }
        });
    });
})();

