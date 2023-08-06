$(document).ready(function() {

    var actual_url = document.location.href;

    /* 
     * Image popup 
     */

    $('.captioned img,img.captioned').each(function(i) {
        var src = $(this).attr('src');
        var parts = src.split('/');

        if (src.indexOf('@@images')>=0) {
            /* e.g. ajung.gif/@@images/1bc922b8-ca26-4b50-a9f6-3524e46fde36.jpeg */
            src = parts.slice(0, parts.length-2).join('/');
        }
        else {
            // remove trailing scale
            var scale = parts[parts.length-1];
            if (scale.indexOf('image_') > -1 || scale == 'image') {
                src = parts.slice(0, parts.length-1).join('/');
            }
        }
        
        $(this).wrap('<a class="img-fullscreen" href="' + src + '/@@image_fullscreen_overlay" ></a>');
    });

    $('.img-fullscreen').each(function(i) {
            console.log('done');
        var anchor = $(this);
        anchor.prepOverlay({
                subtype: 'ajax',
                width: 'auto'
            }
        );
    });


    /*
     * Table overlay
     */

    $('table.table-popup').each(function(i) {
        var table = $(this);
        var id = table.attr('id');
        caption = table.find('caption');
        caption_text = caption.html();
        caption_text = caption_text==null ? '' : caption_text;
        $('<a class="table-popup" href="' + actual_url + '/@@show_table?id=' + id +'")">' + caption_text + '</a>').insertBefore(table);
        table.hide();
    });

    $('a.table-popup').each(function(i) {
        var anchor = $(this);
        anchor.prepOverlay({
                subtype: 'ajax',
                width: '90%'
            }
        );
    });


})
