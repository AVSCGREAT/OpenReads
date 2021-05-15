function error(errordiv, input, message) {
    $(errordiv).show().html(message);
    $(input).focus();
    return false;
}

function update_len() {
    var len = $('#excerpts-excerpt').val().length;
    var color;
    if (len > 2000) {
        color = '#e44028';
    } else {
        color = 'gray';
    }
    $('#excerpts-excerpt-len').html(2000 - len).css('color', color);
}

export function initEditionEditPage(){
    $(function() {
        ['#languages','#translated_from_languages'].forEach((selector)=>{
            $(selector).setup_multi_input_autocomplete(
                'input.language-autocomplete',
                render_language_field,
                { endpoint: '/languages/_autocomplete' },
                {
                    max: 6,
                    formatItem: render_language_autocomplete_item
                });
        })

        const worksDataset = document.querySelector('#works').dataset;
        $('#works').setup_multi_input_autocomplete(
            'input.work-autocomplete',
            render_work_field,
            {
                endpoint: '/works/_autocomplete',
                addnew: worksDataset.isprivilegeduser === 'true',
                new_name: worksDataset.newWorkText,
            },
            {
                minChars: 2,
                max: 11,
                matchSubset: false,
                autoFill: false,
                formatItem: render_work_autocomplete_item
            });
    });
}

export function initEditRow(){
    document.querySelector('#add_row_button').addEventListener('click', ()=>add_row('website'));
}

/**
 * Adds another input box below the last when adding multiple websites to user profile.
 * @param string name - when prefixed with clone_ should match an element identifier in the page. e.g. if name would refer to clone_website
**/
function add_row(name) {
    const inputBoxes = document.querySelectorAll(`#clone_${name} input`);
    const inputBox = document.createElement('input');
    inputBox.name = `${name}#${inputBoxes.length}`;
    inputBox.type = 'text';
    inputBoxes[inputBoxes.length-1].after(inputBox);
}

function show_hide_title() {
    if ($('#excerpts-display .repeat-item').length > 1) {
        $('#excerpts-so-far').show();
    } else {
        $('#excerpts-so-far').hide();
    }
}


export function initEdit() {

    $('#excerpts').repeat({
        vars: {
            prefix: 'work--excerpts',
        },
        validate: function(data) {
            if (!data.excerpt) {
                return error('#excerpts-errors', '#excerpts-excerpt', 'Please provide an excerpt.');
            }
            if (data.excerpt.length > 2000) {
                return error('#excerpts-errors', '#excerpts-excerpt', 'That excerpt is too long.')
            }
            $('#excerpts-errors').hide();
            return true;
        }
    });

    // update length on every keystroke
    $('#excerpts-excerpt').keyup(update_len);

    // update length on add.
    $('#excerpts')
        .bind('repeat-add', update_len)
        .bind('repeat-add', show_hide_title)
        .bind('repeat-remove', show_hide_title);

    // update length on load
    update_len();
    show_hide_title();
}
