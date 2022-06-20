import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

const socket = io.connect(document.location.origin);

socket.on("messageAlert", function(data) {
    // make a desktop notification

    console.log("Message alert received.");

    if (!Notification) {
        alert('Desktop notifications not available in your browser.');
    } else {
        if (Notification.permission !== 'granted')
        Notification.requestPermission();
        
        if (Notification.permission !== 'granted')
        Notification.requestPermission();
        else {
        var notification = new Notification('You\'ve been mentioned.', {
            icon: document.location.origin + '/static/pngs/logo.png',
            body: 'Hey! ' + data.mentioner + ' mentioned you in Discussion.'
        });
        notification.onclick = function() {
            window.open(document.location.origin + '/discussion');
        }};
    }
});

window.onbeforeunload = function () {
	socket.emit('client_disconnecting', {});
}

console.log("Loaded Push Notifications.");