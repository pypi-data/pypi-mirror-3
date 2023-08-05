/* collective.atimages.transformtoolbar JavaScript for transforming images via AJAX */

jQuery(document).ready(function() {
    // Get kss-spinner element (or create it) for future use
    var spinner = jQuery('#kss-spinner');
    if(spinner.length==0) {
        jQuery('html body').append('<div id="kss-spinner" style="display: none; "><img src="./spinner.gif" /></div>');
        spinner = jQuery('#kss-spinner');
    }
    
    // Get every transformation link and turn it AJAX-powered
    jQuery('#atimage_transformtoolbar a').each(function(idx, el) {
        el = jQuery(el);
        // bind click event
        el.click(function(event) {
            // stop default click of links (i.e. open url in href)
            event.preventDefault();
            event.stopPropagation();
            // show spinner
            spinner.show();
            // make sure we get a handle to the <a /> element (event.target could be the image inside)
            var target = jQuery(event.target).closest('a');
            // make an ajax call
            jQuery.ajax({
                url: target.attr('href') + '&ajax=1', // to the same link url with an extra parameter
                cache: false, // prevent undesired results by turning cache off
                complete: function(data, status) {
                    var errorContainer = jQuery('#transformtoolbar_error');
                    var json = eval('(' + data.responseText + ')');
                    var success = json.success;
                    if(success) {
                        // transform succeeded: reload the image (double selector for Plone 4 and Plone 3 compatibility)
                        var img = jQuery('#content-core a[href$=image_view_fullscreen] img[src*=image], #content a[href$=image_view_fullscreen] img[src*=image]');
                        var timestamp = new Date().getTime();
                        var img_src = img.attr('src').indexOf('?')==-1 ? img.attr('src') : img.attr('src').substring(0, img.attr('src').indexOf('?'));
                        jQuery.get(img_src + '/tag', 'ts=' + timestamp, function(data, status, request) {
                            data = data.replace(img_src, (img_src + '?ts= ' + timestamp));
                            img.replaceWith(data);
                        });
                        // and hide error if we had one
                        errorContainer.hide();
                    } else {
                        // transform failed: inform the error
                        var error = json.error;
                        var errorContainer = jQuery('#transformtoolbar_error');
                        if(errorContainer.length==0) {
                            jQuery('#atimage_transformtoolbar').before('<dl id="transformtoolbar_error" class="portalMessage error"><dt>' + error.title + '</dt><dd>' + error.msg + '</dd></dl>');
                        } else {
                            errorContainer.show().children('dd').text(error);
                        }
                       
                    }
                    spinner.hide();

                }
            });
        });
    });
});

