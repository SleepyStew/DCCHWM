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
  document.getElementById('messages').innerHTML += '<div class="message"><span class="username">' + data.username + '</span>' + data.message + '</div>';
  document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

  var converter = new showdown.Converter();
  var messages = document.getElementsByClassName("message")
  messages[messages.length - 1].innerHTML = converter.makeHtml(messages[messages.length - 1].innerHTML);
  messages[messages.length - 1].lastChild.style.display = 'inline';
});

document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
