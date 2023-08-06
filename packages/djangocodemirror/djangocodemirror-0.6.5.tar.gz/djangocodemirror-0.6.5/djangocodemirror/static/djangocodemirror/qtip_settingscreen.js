/*
 * Modal screen form to edit settings
 *
 * Use qTip to make a modal screen from the html iframe view
*/
window.createSettingScreen = function(element_instance, url) {
    // Create the modal
    $(element_instance).qtip({
        id: 'djangocodemirror_settings_screen', // Since we're only creating one modal, give it an ID so we can style it
        overwrite: true,
        content: {
            // Set the text to an image HTML string with the correct src URL to the loading image you want to use
            text: '<img class="throbber" src="'+FOOTIP+'" alt="Loading .." />',
            ajax: {
                url: url
            },
            title: {
                text: 'Your settings',
                button: true
            }
        },
        position: {
            my: 'center', // ...at the center of the viewport
            at: 'center',
            target: $(window)
        },
        show: {
            event: 'click', // Show it on click...
            ready: true,
            solo: true, // ...and hide all other tooltips...
            modal: true // ...and make it modal
/*            event: 'click', // Show it on click...
            solo: true, // ...and hide all other tooltips...
            //modal: true // ...and make it modal
            modal: {
                on: true, // Make it modal (darken the rest of the page)...
                blur: false // ... but don't close the tooltip when clicked
            }*/
        },
        events: {
            render: function(event, api) {
                //pass
            }
        },
        //hide: false,
        style: 'ui-tooltip-light ui-tooltip-rounded'
    })
    .removeData('qtip');
};
