import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

const socket = io.connect(document.location.origin);

document.getElementById('messageinput').addEventListener("keypress", function(event) {
    if (event.key === "Enter" && event.shiftKey === false) {
      event.preventDefault();
      document.getElementById("sendmessage").click();
    }
}); 

document.getElementById('sendmessage').addEventListener('click', function() {
  socket.emit('chatmessage', { message: document.getElementById('messageinput').value });
  document.getElementById('messageinput').value = '';
});

var prev = "";

socket.on('chatmessage', function(data) {
  if (prev == data.username) {
    document.getElementById('messages').innerHTML += '<div class="message join"><span class="username">' + data.username + '</span>: ' + data.message + '</div>';
  } else {
    document.getElementById('messages').innerHTML += '<div class="message"><span class="username">' + data.username + '</span>: ' + data.message + '</div>';
  }
  document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
  prev = data.username;
});

document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
