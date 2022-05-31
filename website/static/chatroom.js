import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

const socket = io.connect(document.location.origin);

let setting_deleted_messages = document.getElementById('show-deleted-messages').innerText;

console.log("Websocket connected");

function deleteMessage(id) {
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

socket.on('chatmessage', function(data) {
  let username_element = document.createElement('span')
  username_element.innerText = data.username
  username_element.classList.add("username")
  let new_message = document.createElement('div')
  new_message.classList.add("message")
  new_message.classList.add("list-group-item")
  new_message.id = data.id
  new_message.innerText = data.message
  new_message.prepend(username_element)
  document.getElementById('messages').insertBefore(new_message, new_message.nextSibling)
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
  if (setting_deleted_messages == "show") {
    document.getElementById(data.id.id).innerHTML = document.getElementById(data.id.id).getElementsByClassName("username")[0].outerHTML + "[message deleted]";
  } else {
    document.getElementById(data.id.id).remove();
  }
});

document.querySelectorAll('.delete-message').forEach(element => {
  element.addEventListener('click', function() {
    deleteMessage(element.parentElement.parentElement.id);
  });
});

document.querySelectorAll('.message').forEach(message => {
  if (message.getElementsByClassName("username")[0].innerText == document.getElementById("my-username").innerText) {
    message.classList.add("mine")
  }
});

window.onload = function() {
  document.querySelectorAll('.message').forEach(message => {
      message.style.display = "";
  });
  document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
};

$('body').on('keydown', function() {
  var input = $('#messageinput');
  if(!input.is(':focus')) {
      input.focus();
  }
});