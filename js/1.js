// $(document).on('click', '#url_button', function() {
$(document).ready(function() {
    $.post('/get_url_list', {}, function(data) {
        data = JSON.parse(data)
        // console.log(data)
        $('#url_list').empty()
        $('#url_list').append('<tr><td></td><td><input id="add_url_input" style="float:left; margin-right:10px"></td>' +
            '<td><button id="add_url_button" style="float:left; margin-right:10px">Добавить ссылку</button></td></tr>')
        for (var i = 0; i < data.length; ++i) {
            $('#url_list').append('<tr><td style="float:left; margin-right:10px">' + data[i][0] + '</td><td style="float:left; margin-right:10px">' 
                + data[i][1] + '</td><td><button id="delete_url" style="margin-right:10px" param="' + data[i][0] + '">Удалить ссылку</button></td>' +
                '<td><div id="update_status' + data[i][0] + '" class="show_update" param="' + data[i][0] + '" updates="no">Обновлений нет</div></td></tr>')
        }
    })
    $('#get_updates').click()
})

$(document).on('click', '#delete_url', function() {
    $.post('/rm_url_from_list', {'id': $(this).attr('param')}, function(data) {
        console.log(data)
    })
    window.location.reload();
})

$(document).on('click', '#get_updates', function() {
    $.post('/get_updates', {'date_begin': $('#date_begin').val(), 'date_end': $('#date_end').val()}, function(data) {
        data = JSON.parse(data)
        for (i in data) {
            $('#update_status' + data[i]).html('<a style="text-decoration: underline; cursor: default">Обновления</a> есть').attr('updates', 'yes')
        }
    })
})

$(document).on('click', '.show_update', function() {
    console.log('clicked')
    if ($(this).attr('updates') == 'yes')
        $.post('/get_update_by_id_and_dates', {'id': $(this).attr('param'), 'date_begin': $('#date_begin').val(), 'date_end': $('#date_end').val()}, function(data){
            $('#diff_data').remove()
            $('#normal_body').hide()
            $('body').append('<div id="diff_data" style="position:relative; z-index:999; max-width:1000px; border: 1px solid grey">' + 
                '<button style="float:right" id="diff_close">X</button>' + data + '</div>')
        })
})

$(document).on('click', '#diff_close', function() {
    $('#diff_data').remove()
    $('#normal_body').show()
})


$(document).on('click', '#add_url_button', function() {
    console.log('clicked')
    var urlregex = /^(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})/;
    var url = $('#add_url_input').val()
    if (urlregex.test(url))
        $.post('/add_url', {'url': url}, function(data){
            console.log(data)
        })    
    window.location.reload()
})

