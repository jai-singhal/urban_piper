var taskSocket = new ReconnectingWebSocket('ws://' + window.location.host + '/ws/task/');
function connect() {
    taskSocket.onopen = function open() {
        console.log('WebSockets connection created.');
        taskSocket.send(JSON.stringify({
            "event": "JOIN",
            "message": "dp"
        }));
    };

    taskSocket.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    };
    // Sending the info about the room
    taskSocket.onmessage = function (e) {
        let data = JSON.parse(e.data);
        data = data["payload"];
        let message = data['message'];
        let event = data["event"];
        switch (event) {
            case "NEW_TASK":
                display_new_task(taskSocket, message);
                break;
            case "TASK_ACCEPTED":
                display_accepted_task(taskSocket, message);
                break;
            case "TASK_PENDING":
                alert(message)
                break;
            case "TASK_COMPLETED_ACK":
                remove_accepted_card(message);
                break;
            case "TASK_DECLINED_ACK":
                remove_accepted_card(message);
                break;

            default:
                console.log("No event")
        }
    };

    if (taskSocket.readyState == WebSocket.OPEN) {
        taskSocket.onopen();
    }
}

connect();

$(document).on('click', ".task_completed", function () {
    let message = {
        id: $(this).parents(".card").attr("data-id"),
    }
    task_completed(taskSocket, message);
});

$(document).on('click', ".task_declined", function () {
    let message = {
        id: $(this).parents(".card").attr("data-id"),
    }
    task_declined(taskSocket, message);
});




function task_accepted(taskSocket, message) {
    taskSocket.send(JSON.stringify({
        "event": "TASK_ACCEPTED",
        "message": message
    }));
}

function task_completed(taskSocket, message) {
    taskSocket.send(JSON.stringify({
        "event": "TASK_COMPLETED",
        "message": message
    }));
}


function task_declined(taskSocket, message) {
    taskSocket.send(JSON.stringify({
        "event": "TASK_DECLINED",
        "message": message
    }));
}


function display_new_task(taskSocket, message) {
    let html_content;
    if (message) {
        html_content = `<div class = 'card'>
            <div class = "card-header">
                <p>New Task Recieved:
                        Priority: <span class = "text-danger"> ${message["priority"]}</span>
                </p>
            </div>
            <div class = "card-body">
                <h5 class="card-title">${message["title"]}</h5>
                <p>Created at: ${formatDate(new Date(message["creation_at"])) }</p>
            </div>
            <div class = "card-footer">
                <button id = "task_accept" 
                    class = "btn btn-primary float-right">Accept</button>
        </div>`;
    } else {
        html_content = `
            <div class='card'>
                <div class="card-body">
                    <h6 class="text-danger">No new Task available for you right now</h6>
                </div>
            </div>
        `;
    }

    $("#new_task_card").html(html_content);
    $("#task_accept").click(function () {
        task_accepted(taskSocket, message);
    })
}

function display_accepted_task(taskSocket, message) {
    if ($("#no_accepted_task").length) {
        $("#no_accepted_task").remove();
    }

    $("#task_accepted_body").prepend(`
        <div class='card' data-id = ${message["id"]}>
        <div class="card-body" >
            <h5 class="card-title">${message["title"]}</h5>
            <p>Created at: ${formatDate(new Date(message["creation_at"]))}</p>
        </div>
        <div class="card-footer">
            <button class="btn btn-primary dp_btn float-right task_completed">
                Complete
            </button>
            <button class="btn btn-danger dp_btn float-right task_declined">
                Decline
            </button>
        </div>
    </div>
    `)
}

function remove_accepted_card(message) {
    $(`div.card[data-id=${message["id"]}]`).remove();
    if (!$.trim($("#task_accepted_body").html()).length) {
        $("#task_accepted_body").html(`
            <h6 class="text-danger" id = "no_accepted_task">
                You haven't accepted any Task
            </h6>
        `);
    }
}
