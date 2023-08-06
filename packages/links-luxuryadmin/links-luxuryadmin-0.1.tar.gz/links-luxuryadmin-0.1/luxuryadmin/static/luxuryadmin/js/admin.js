/**
 * Converts the given data structure to a JSON string.
 * Argument: arr - The data structure that must be converted to JSON
 * Example: var json_string = array2json(['e', {pluribus: 'unum'}]);
 *          var json = array2json({"success":"Sweet","failure":false,"empty_array":[],"numbers":[1,2,3],"info":{"name":"Binny","site":"http:\/\/www.openjs.com\/"}});
 * http://www.openjs.com/scripts/data/json_encode.php
 */
function array2json(arr) {
    var parts = [];
    var is_list = (Object.prototype.toString.apply(arr) === '[object Array]');

    for(var key in arr) {
        var value = arr[key];
        if(typeof value == "object") { //Custom handling for arrays
            if(is_list) parts.push(array2json(value)); /* :RECURSION: */
            else parts[key] = array2json(value); /* :RECURSION: */
        } else {
            var str = "";
            if(!is_list) str = '"' + key + '":';

            //Custom handling for multiple data types
            if(typeof value == "number") str += value; //Numbers
            else if(value === false) str += 'false'; //The booleans
            else if(value === true) str += 'true';
            else str += '"' + value + '"'; //All other things
            // :TODO: Is there any more datatype we should be in the lookout for? (Functions?)

            parts.push(str);
        }
    }
    var json = parts.join(",");
    
    if(is_list) return '[' + json + ']';//Return numerical JSON
    return '{' + json + '}';//Return associative JSON
}

$.fn.clearForm = function() {
  return this.each(function() {
    var type = this.type, tag = this.tagName.toLowerCase();
    if (tag == 'form')
      return $(':input',this).clearForm();
    if (type == 'text' || type == 'password' || tag == 'textarea')
      this.value = '';
    else if (type == 'checkbox' || type == 'radio')
      this.checked = false;
    else if (tag == 'select')
      this.selectedIndex = 0;
  });
};

var saveProduct = function(button, data, url, callback) {
    button.attr('disabled', 'disabled');
    $.post(url, data, function(response) {
        if(response.success) {
            callback(response, function() {
                window.location.reload();
            });
        } else {
            alert('Saving product failed!');
        }

        button.removeAttr('disabled');
    }, 'json');
}

var updatePhotos = function(url, product_pk, rows, callback) {
    var images = []
    var selected = $("input[@name=image]:checked", rows.parent()).val()
    for (var i = 0, r; r = rows[i]; i++) {
        filename = $('input[type=radio]' , r).val()
        image = {
            filename: filename
        };
        if (selected == filename) {
            image['selected'] = true;
        } else {
            image['selected'] = false;
        }
        images.push(image);
    }
    data = {
        pk: product_pk,
        images: array2json(images)
    }
    $.post(url, data, function(response) {
        callback(response);
    }, 'json');
}

var showInfoRow = function(t) {
    row = t.closest('tr').next();
    t.removeClass('editInfoButton');
    t.addClass('editInfoButtonSelected');
    row.show();
}
var hideInfoRow = function(t) {
    row = t.closest('tr').next();
    t = $('.editInfoButtonSelected', t.closest('tr'));
    console.log(t);
    t.removeClass('editInfoButtonSelected');
    t.addClass('editInfoButton');
    row.hide();
}

var showImageRow = function(t) {
    row = t.closest('tr').next().next();
    t.removeClass('editImagesButton');
    t.addClass('editImagesButtonSelected');
    row.show();
}

var hideImageRow = function(t) {
    row = t.closest('tr').next().next();
    t = $('.editImagesButtonSelected', t.closest('tr'));
    console.log(t);
    t.removeClass('editImagesButtonSelected');
    t.addClass('editImagesButton');
    row.hide();
}

$(function() {
    /**
     * File uploads are pretty horrible.
     */
    $('input[type="file"]').on('change', function(event) {
        document.body.style.cursor = "wait";
        var form_data = new FormData();
        var xhr = new XMLHttpRequest();
        var t = $(this);
        var rows = $('.productImageRows', t.parent());
        var files = event.target.files;
        var uploaded = function(response) {
            response = $.parseJSON(response);
            for (var i = 0, f; f = response['images'][i]; i++) {
                rows.append(ich.productImageRow(f));
                document.body.style.cursor = "default";
            }

        };
        for (var i = 0, f; f = files[i]; i++) {
            form_data.append(f.name, f);
        }
        xhr.open('POST', t.attr('url'), true);
        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                uploaded(xhr.response);
            }
        };
        xhr.send(form_data);
        form_data = new FormData()
        event.preventDefault();
    })

    $('#saveNewProductButton').on('click', function(event) {
        event.preventDefault();
        var form = $('#newProductInfoForm');
        var data = form.toObject();
        var url = form.attr('action');
        saveProduct($(this), data, url, function(response, callback) {
            var container = $('#newProductImagesContainer');
            var url = container.attr('url');
            var product_pk = response.pk;
            updatePhotos(url, product_pk, $('.productImageRow', container), callback);
        });
    });

    $('.infoUpdateButton').on('click', function(event) {
        event.preventDefault();
        var form = $(this).closest('form');
        var data = form.toObject();
        var url = form.attr('action');
        saveProduct($(this), data, url, function(response, callback) {
            window.location.reload();
        });
    });

    $('.productEditRow input, .productEditRow select').on('change', function(event) {
        event.preventDefault();
        var row = $(this).closest('tr');
        var cat = $('select[name=category]');
        var data = {
            category: $('select[name=category] option:selected', row).val(),
            featured: $('input[name=featured]:checked', row).val(),
            sold: $('input[name=sold]:checked', row).val()
        };
        saveProduct($(this), data, row.attr('action'), function(response, callback) {
            window.location.reload();
        });
    });

    $('.imageUpdateButton').on('click', function(event) {
        event.preventDefault();
        var t = $(this);
        var row = t.closest('tr');
        var rows = $('.productImageRow', row);
        var url = row.attr('url');
        var product_pk = row.attr('product_pk');
        updatePhotos(url, product_pk, rows, function() { window.location.reload() });
    });

    $('body').on('click', 'a.deleteButton', function(event) {
        event.preventDefault();
        row = $(this).closest('.productImageRow');
        row.fadeOut(function() {
            row.remove();
        });
    })

    var limit = 400;
    $('.limited').on('keyup', function() {
        var t = $(this);
        var count = $('span.count', t.parent());
        var length = $(this).val().length;
        count.text(length);
        if(length >= limit) {
            t.val(t.val().substring(0, limit));
        }
    })

    $('tr.editInfoRow, tr.editImagesRow').hide();

    // Open edit row.
    $('body').on('click', 'a.editInfoButton', function(event) {
        event.preventDefault();
        showInfoRow($(this));
        hideImageRow($(this));
    });

    // Close edit row.
    $('body').on('click', 'a.editInfoButtonSelected', function(event) {
        event.preventDefault();
        hideInfoRow($(this));
    });

    // Open image row.
    $('body').on('click', 'a.editImagesButton', function(event) {
        event.preventDefault();
        showImageRow($(this));
        hideInfoRow($(this));
        
    });

    // Close image row.
    $('body').on('click', 'a.editImagesButtonSelected', function(event) {
        event.preventDefault();
        hideImageRow($(this));
    });
});

