// Отправка сообщения на сервер
function PublishForm(form, method) {
    let method_url = 'http://localhost:8000/' + method

    function sendMessage(message) {
        fetch(method_url, {
            method: 'POST',
            headers: {"content-type": "application/json"},
            body: JSON.stringify({"message": message})
        });
    }

    form.onsubmit = function () {
        let message = form.message.value;
        if (message) {
            form.message.value = '';
            sendMessage(message)
        }
        return false
    };
}

// Получение сообщений через polling
function SubscribePane(elem, method) {
    let method_url = 'http://localhost:8000/' + method

    function showMessage(message) {
        if (typeof message != "undefined") {
            let messageElem = document.createElement('div');
            messageElem.append(message);
            elem.append(messageElem);
        }
    }

    async function subscribe() {
        let response

        try {
            response = await fetch(method_url)
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (e)
        {
            console.log(e)
            await new Promise(resolve => setTimeout(10000));
            await subscribe();
        }

        if (response.status === 502) {
            showMessage("RECONNECT")
            await subscribe();
        } else if (response.status !== 200) {
            showMessage(response.statusText);
            await new Promise(resolve => setTimeout(resolve, 1000));
            await subscribe();
        } else {
            let message = (await response.json())['message']
            console.log(message);
            showMessage(message);
            await subscribe();
        }
    }

    subscribe()
}

function SubscribePaneSSE(elem) {
    const evtSource = new EventSource("http://127.0.0.1:8000/stream")

    function showMessage(message) {
        if (typeof message != "undefined") {
            let messageElem = document.createElement('div');
            messageElem.append(message);
            elem.append(messageElem);
        }
    }

    evtSource.addEventListener("new_message", function (event){
        // Получаем и выводим сообщения
        console.log(event.data)
        showMessage(event.data)
    });

    evtSource.addEventListener("end_event", function (event){
        console.log(event.data)
        showMessage(event.data)
        evtSource.close()
    });


    return () => {
        evtSource.close();
    };
}
