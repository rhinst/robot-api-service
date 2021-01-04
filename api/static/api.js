var base_url = "http://localhost:8080"

function motor_drive() {
    $.ajax({
        "url": base_url + "/motor/drive",
        "type": "POST",
        "data": JSON.stringify({
            "speed": 1.0,
            "direction": "forward"
        }),
        processData: false,
        "contentType": "application/json",
        "dataType": "json"
    });
}

function motor_stop() {
    $.ajax({
        "url": base_url + "/motor/stop",
        "type": "POST"
    });
}


function say(phrase) {
    $.ajax({
        "url": base_url + "/speech/say",
        "type": "POST",
        "data": JSON.stringify({
            "phrase": phrase
        }),
        processData: false,
        "contentType": "application/json",
        "dataType": "json"
    })
}

function listen_phrase() {
    $.ajax({
        "url": base_url + "/listen/phrase",
        "type": "POST",
        "data": "{}",
        processData: false,
        "contentType": "application/json",
        "dataType": "json",
        "success": function() {

        }
    }).done(function(data) {
        $('#listened_phrase').innerHTML(data)
    });
}

