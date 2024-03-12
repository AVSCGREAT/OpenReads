import { ungettext, ugettext } from './i18n';

/**
 * jQuery plugin to add form validations.
 *
 * To enable, add class="validate" to the form and add required validations in class to the input elements.
 * Available validations are: required, email, and publish-date.
 *
 * Example:
 *      <form name="create" class="validate">
 *          Username: <input type="text" class="required" name="username" value=""/> <br/>
 *          E-mail: <input type="text" class="required email" name="username" value=""/> <br/>
 *          Password: <input type="text" class="required" name="username" value=""/> <br/>
 *          <input type="submit" name="submit" value="Register"/>
 *      </form>
 */
export default function initValidate() {


    // validate publish-date to make sure the date is not in future
    // used in templates/books/add.html
    jQuery.validator.addMethod('publish-date', function(value) {

        // we allow the year dates 'xxxx', '199x', '19xx' date variants: https://github.com/internetarchive/openlibrary/issues/5254
        // The Regex: https://regex101.com/r/t1oiEv/1
        var token_xxxx = /^([1-9][x0-9]{0,3}|[x]{4})$/.exec(value);

        // if it doesn't have even three digits then it can't be a future date
        //var tokens = /(\d{3,})/.exec(value);

        //var year = new Date().getFullYear();
        return token_xxxx;

        // The previous check that verifies if a CE date is not more than a year in the future. This is disabled due to bugs such as '199xxx'
        //return token_xxxx || (tokens && tokens[1] && parseInt(tokens[1]) <= year + 1); // allow one year in future.
    },
    'Are you sure that\'s the published date?'
    );

    $.validator.messages.required = '';
    $.validator.messages.email = ugettext('Are you sure that\'s an email address?');


    $.fn.ol_validate = function(options) {
        var defaults = {
            errorClass: 'invalid',
            validClass: 'success',
            errorElement: 'span',
            invalidHandler: function(form, validator) {
                var errors = validator.numberOfInvalids();
                var message;
                if (errors) {
                    message = ungettext(
                        'Hang on... you missed a bit. It\'s highlighted below.',
                        'Hang on...you missed some fields. They\'re highlighted below.',
                        errors);

                    $('div#contentMsg span').html(message);
                    $('div#contentMsg').show().fadeTo(3000, 1).slideUp();
                    $('span.remind').css('font-weight', '700').css('text-decoration', 'underline');
                } else {
                    $('div#contentMsg').hide();
                }
            },
            highlight: function(element, errorClass) {
                $(element).addClass(errorClass);
                $(element.form)
                    .find(`label[for=${element.id}]`)
                    .addClass(errorClass);
            },
            unhighlight: function(element, errorClass) {
                $(element).removeClass(errorClass);
                $(element.form)
                    .find(`label[for=${element.id}]`)
                    .removeClass(errorClass);
            }
        };
        $(this).validate($.extend(defaults, options));
    };

}
