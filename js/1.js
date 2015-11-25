$( document ).ready(function() {
    $('button').click(function() {
        console.log('clicked')
        $.post("/", { name: "John", time: "2pm" }, function(data) {
            console.log(data)
        })
    })
})
