let aliveSecond = 0;
let heartBeatRate = 1000;
let pubnub;
let appChannel = "motion_channel";

// Function to check server status and update connection status
function time() {
    let d = new Date();
    let currentSecond = d.getTime();
    if (currentSecond - aliveSecond > heartBeatRate + 1000) {
        document.getElementById("connection_id").innerHTML = "DEAD";
    } else {
        document.getElementById("connection_id").innerHTML = "ALIVE";
    }
    setTimeout(time, 1000);
}

// Function to keep the server connection alive
function keepAlive() {
    fetch('/keep_alive')
        .then(response => {
            if (response.ok) {
                let date = new Date();
                aliveSecond = date.getTime();
                return response.json();
            }
            throw new Error('Server offline');
        })
        .catch(error => console.log(error));
    setTimeout(keepAlive, heartBeatRate);
}


// Publish a message to the PubNub channel
const publishMessage = async (message) => {
    const publishPayload = {
        channel: appChannel,
        message: message,
    };
    await pubnub.publish(publishPayload);
};

// Set up PubNub for real-time communication
function setupPubNub() {
    pubnub = new PubNub({
        publishKey: "pub-c-48f6b9c1-0ffc-435b-a55e-d52776778f65",
        subscribeKey: "sub-c-a601ad79-0e0f-450f-a941-026ebac0a79e",
        uuid: "teck-pi",
    });

    pubnub.addListener({
        status: (statusEvent) => {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Connected to PubNub");
            }
        },
        message: (messageEvent) => {
            // Handle incoming motion or LED status updates
            if (messageEvent.message.motion_count !== undefined) {
                document.getElementById("motion_id").innerText = messageEvent.message.motion_count;
            }
            if (messageEvent.message.led_status !== undefined) {
                document.getElementById("led_status").innerText = messageEvent.message.led_status ? "ON" : "OFF";
            }
        },
    });

    pubnub.subscribe({ channels: [appChannel] });
}

// Simplify granting access (if needed)
function grantAccess(ab) {
    const userId = ab.id.split("-")[2];
    const readState = document.getElementById(`read-user-${userId}`).checked;
    const writeState = document.getElementById(`write-user-${userId}`).checked;

    fetch(`/grant-${userId}-${readState}-${writeState}`, { method: "POST" })
        .then(response => response.json())
        .then(responseJson => {
            console.log("Access granted:", responseJson);
            if (responseJson.hasOwnProperty('token')) {
                pubnub.setToken(responseJson.token);
                pubnub.setCipherKey(responseJson.cipher_key);
                pubnub.setUUID(responseJson.uuid);
            }
        });
}

// Initialize the application on page load
window.onload = function () {
    keepAlive();
    time();
    setupPubNub();
};
