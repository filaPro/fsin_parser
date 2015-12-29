// $(document).on('click', '#url_button', function() {
$(document).ready(function() {
    $.post('/get_url_list', {}, function(data) {
        data = JSON.parse(data)
        // console.log(data)
        $('#url_list').empty()
        $('#url_list').append('<tr><td></td><td><input id="add_url_input" style="float:left; margin-right:10px"></td>' +
            '<td><button id="add_url_button" style="float:left; margin-right:10px">Добавить ссылку</button></td></tr>')
        for (var i = 0; i < data.length; ++i) {
            $('#url_list').append('<tr><td style="float:left; margin-right:10px">' + (1+i) + '</td>'+
					'<td style="float:left; margin-right:10px">'+
						'<a target=_blank href="'+data[i].url+'">'+ data[i].url + '</a>' +
					'</td><td><button id="delete_url" style="margin-right:10px" param="' + data[i].id + '">Удалить ссылку</button></td>' +
					'<td><div id="update_status' + data[i].id + '" class="show_update" param="' + data[i].id + '" updates="no">Обновлений нет</div></td></tr>')
        }
    })
    $('#date_begin').val('2010-01-01')
    $('#date_end').val('2020-01-01')
    $('#get_updates').click()
})

$(document).on('click', '#delete_url', function() {
    $.post('/rm_url_from_list', {'id': $(this).attr('param')}, function(data) {
        console.log(data)
    })
    window.location.reload();
})

$(document).on('click', '#get_updates', function() {
    if ($('#date_begin').val() == '' && $('#date_end').val() == '') {
        alert('Даты введены некорректно.')
        return
    }
    console.log('clicked')
    $.post('/get_updates', {'date_begin': $('#date_begin').val(), 'date_end': $('#date_end').val()}, function(data) {
        data = JSON.parse(data)
        console.log(data)
        for (i in data) {
            var ln = $('#update_status' + data[i].page)
			ln.html('<a style="text-decoration: underline; cursor: pointer">Обновления</a> есть').attr('updates', 'yes')
            if (data[i].readed == 'FALSE')
                ln.css('background-color', '#7FFF00');
        }
    })
})

$(document).on('click', '.show_update', function() {
    console.log('clicked')
    if ($(this).attr('updates') == 'yes') {
        $(this).css('background-color', 'white')
        $.post('/get_update_by_id_and_dates', {'id': $(this).attr('param'), 'date_begin': $('#date_begin').val(), 'date_end': $('#date_end').val()}, function(data) {
            $('#diff_data').remove()
            $('#normal_body').hide()
            $('body').append('<div id="diff_data" style="position:relative; z-index:999; max-width:1000px; border: 1px solid grey; margin: auto;">' + 
                '<button style="float:right" id="diff_close">X</button>' + data + '</div>')
        })
        $.post('/set_readed', {'id': $(this).attr('param')})
    }  
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
    else
        alert('Ссылка введена некоррректно.')
    window.location.reload()
})

$(document).on('click', '#get_status_string', function() {
    $.post('/get_status_string', {}, function(data) {
        $('#status_div').html(data)
    })
})
