function define_user_and_access() {

    // get all the inputs into an array.
    var $inputs = $('#access_form :input');

    // not sure if you wanted this, but I thought I'd add it.
    // get an associative array of just the values.
    var values = [];
    $inputs.each(function () {
        data_id = this.id;
        data_name = this.name
        data_checked = $(this).is(":checked");
        data_id_description = String(this.id).concat('_description')
        data_description = $('#' + data_id + '_description').text();
        values.push({ name: data_name, id: data_id, checked: data_checked, description: data_description })
    });

    var server_data = {
        "exp_list": values,
        "participant": $('#participantId').val()
    };

    $.ajax({
        url: "http://localhost:5000/define_user_and_access",
        type: 'POST',
        data: JSON.stringify(server_data),
        success: function (response) {
            console.log(response)
            showMessage("success", "Settings updated properly", 2000);
        },

        error: function (xhr) {
            //Do Something to handle error
            // window.location.href = response;
            showMessage("danger", xhr, 2000);
            console.log("error");
            console.log(xhr);
        }
    });
}


function check_password() {
    password = $('#adminPassword').val();

    $.ajax({
        url: "http://localhost:5000/check_password",
        type: "get", //send it through get method
        data: {
            pass: password
        },
        success: function (response) {
            console.log("success");
            console.log(response)
            if (response.ans == 'False') {
                showMessage("warning", "Wrong password, try again", 2000);
            } else if (response.ans == 'True') {
                window.location.href = '/admin_panel';
            }

        },
        error: function (xhr) {
            //Do Something to handle error
            // window.location.href = response;
            showMessage("danger", xhr, 2000);
            console.log("error");
            console.log(xhr);
        }
    });
}


function exp_went_well() {
    // value = $('#button_name').val();
    // console.log(value)

    $.ajax({
        url: "http://localhost:5000/exp_went_well",
        type: "get", //send it through get method,
        success: function (response) {
            console.log(response);
            window.location.href = '/home';
        },
        error: function (xhr) {
            //Do Something to handle error
            showMessage("danger", xhr, 2000);
            console.log("error");
        }
    });
}


function exp_went_bad() {
    $.ajax({
        url: "http://localhost:5000/exp_went_bad",
        type: "get", //send it through get method,
        success: function (response) {
            console.log(response);
            window.location.href = '/home';
        },
        error: function (xhr) {
            //Do Something to handle error
            showMessage("danger", xhr, 2000);
            console.log("error");
        }
    });
}


function start_exp(action) {
    $.ajax({
        url: "http://localhost:5000/start_exp",
        type: "get",
        data: {
            experiment_to_start: action
        },
        beforeSend: function () {
            $('body').append('<div id="requestOverlay" class="request-overlay"></div>'); /*Create overlay on demand*/
            $("#requestOverlay").show();/*Show overlay*/
        },
        success: function (response) {
            console.log("success");
            console.log(response);
            window.location.href = response.ans;
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(textStatus);
            showMessage("danger", "Technical Error Found, check system logs and/or the console output", 2000);
            console.log(xhr.responseText.ans);
        },

        complete: function () {
            $("#requestOverlay").remove();/*Remove overlay*/
        }
    });
}


function showMessage(_message_class, _message_html, _message_timeout) {
    $("#message-" + _message_class).html(_message_html);
    $("#message-" + _message_class).css("display", "block");
    setTimeout(function () {
        $("#message-" + _message_class).css("display", "none");
    }, _message_timeout);
}
