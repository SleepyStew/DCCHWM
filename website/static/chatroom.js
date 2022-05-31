import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

const socket = io.connect(document.location.origin);

console.log("Websocket connected");

function deleteMessage(id) {
    console.log
    socket.emit('deletemessage', { id: id });
}

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
  document.getElementById('messages').insertAdjacentHTML('beforeend', '<div id="' + data.id + '" class="message list-group-item"><span class="username">' + data.username + '</span>' + data.message + '</div>');
  document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

  var converter = new showdown.Converter();
  var messages = document.getElementsByClassName("message")
  messages[messages.length - 1].innerHTML = converter.makeHtml(messages[messages.length - 1].innerHTML);
  messages[messages.length - 1].lastChild.style.display = 'inline';
  if (document.getElementById("my-username").innerText == document.getElementById(data.id).getElementsByClassName("username")[0].innerText) {
    messages[messages.length - 1].classList.add("mine")
    messages[messages.length - 1].children[0].innerHTML += "<button type=\"button\" class=\"btn-close position-absolute end-0 me-2 delete-message\" alt=\"Delete Note\"></button>"
    document.getElementById(data.id).children[0].lastChild.addEventListener('click', function() {
      deleteMessage(data.id);
    });
  }
});

socket.on('deletemessage', function(data) {
  document.getElementById(data.id.id).innerHTML = document.getElementById(data.id.id).getElementsByClassName("username")[0].outerHTML + "[message deleted]";
});

document.querySelectorAll('.delete-message').forEach(element => {
  element.addEventListener('click', function() {
    deleteMessage(element.parentElement.parentElement.id);
  });
});

document.querySelectorAll('.message').forEach(message => {
  console.log(message.getElementsByClassName("username")[0].innerText);
  console.log(document.getElementById("my-username"));
  if (message.getElementsByClassName("username")[0].innerText == document.getElementById("my-username")) {
    message.classList.add("mine")
  }
});
