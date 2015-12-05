$(document).on('click', '#url_button', function() {
    console.log('clicked')
    $.post('/get_url_list', {}, function(data) {
        data = JSON.parse(data)
        // console.log(data)
        $('#url_list').empty()
        for (var i = 0; i < data.length; ++i) {
            $('#url_list').append('<div><div style="float:left; margin-right:10px">' + data[i][0] + '</div><div style="float:left; margin-right:10px">' 
                + data[i][1] + '</div><button id="delete_url" style="margin-right:10px" param="' + data[i][0] + '">delete</button>' +
                '<button id="update_status' + data[i][0] + '" class="show_update" param="' + data[i][0] + '">no</button></div>')
        }
        $('#url_list').append('<div><input id="add_url_input" style="float:left; margin-right:10px"><button id="add_url_button" style="float:left; margin-right:10px">add</button></div>')
    })
})

$(document).on('click', '#delete_url', function() {
    $.post('/rm_url_from_list', {'id': $(this).attr('param')}, function(data) {
        console.log(data)
    })
})

$(document).on('click', '#get_updates', function() {
    $.post('/get_updates', {'date_begin': $('#date_begin').val(), 'date_end': $('#date_end').val()}, function(data) {
        data = JSON.parse(data)
        for (i in data) {
            console.log($('#update_status' + data[i]).text('yes'))
        }
    })
})

$(document).on('click', '.show_update', function() {
    console.log('clicked')
    if ($(this).text() == 'yes')
        $.post('/get_update_by_id_and_dates', {'id': $(this).attr('param'), 'date_begin': $('#date_begin').val(), 'date_end': $('#date_end').val()}, function(data){
            $('#diff_data').remove()
            $('body').append('<div id="diff_data">' + data + '</div>')
        })
})

$(document).on('click', '#add_url_button', function() {
    console.log('clicked')
    var urlregex = /^(https?|ftp):\/\/([a-zA-Z0-9.-]+(:[a-zA-Z0-9.&%$-]+)*@)*((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}|([a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(:[0-9]+)*(\/($|[a-zA-Z0-9.,?'\\+&%$#=~_-]+))*$/;
    var url = $('#add_url_input').val()
    if (urlregex.test(url))
        $.post('/add_url', {'url': url}, function(data){
            console.log(data)
        })    
})

