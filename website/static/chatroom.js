import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

const socket = io.connect(document.location.origin);

let setting_deleted_messages = document.getElementById('show-deleted-messages').innerText;

let messages_loaded = 100

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
  username_element.style.display = "inline"
  let date_element = document.createElement('span')
  date_element.innerText = " " + data.datetime
  date_element.classList.add("date")
  date_element.style.display = "inline"
  date_element.innerHTML += "<br>"
  let new_message = document.createElement('div')
  new_message.classList.add("message")
  new_message.classList.add("list-group-item")
  new_message.id = data.id
  new_message.innerText = data.message
  new_message.prepend(date_element)
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
    document.getElementById(data.id.id).innerHTML = document.getElementById(data.id.id).getElementsByClassName("username")[0].outerHTML + document.getElementById(data.id.id).getElementsByClassName("date")[0].outerHTML + "[message deleted]";
  } else {
    document.getElementById(data.id.id).remove();
  }
});

socket.on('disconnect', function() {
  location.reload();
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
  document.getElementById('no-more').style.display = "block";
};

$('body').on('keydown', function() {
  var input = $('#messageinput');
  if(!input.is(':focus')) {
      input.focus();
  }
});

let getting_more = false;
document.getElementById("messages").addEventListener("scroll", function() {
  let el = document.getElementById("messages");
  var lastScrollHeight = el.scrollHeight;
  var lastScrollTop = el.scrollTop;
  if (lastScrollTop > 2000 || getting_more) {
    return;
  }
  getting_more = true;
  axios.get('api/get-more-messages?amount=100&from=' + (messages_loaded + 100)).then((_res) => {
    let messages_recieved;
    el = document.getElementById("messages");
    lastScrollHeight = el.scrollHeight;
    lastScrollTop = el.scrollTop;
    if (_res.data.length > 0) {
      if (messages_loaded == 1) {
        messages_recieved = _res.data;
      } else {
        messages_recieved = _res.data.reverse()
      }
    } else {
      document.getElementById("no-more").style.boxShadow = "none";
      document.getElementById("no-more").innerText = "No more messages to display";
      document.getElementById("no-more").classList.add("disabled");
      return
    }
    messages_recieved.forEach(data => {
      if (setting_deleted_messages == "hide" && data.deleted) {
        return;
      }
      let username_element = document.createElement('span')
      username_element.innerText = data.username
      username_element.classList.add("username")
      username_element.style.display = "inline"
      let date_element = document.createElement('span')
      date_element.innerText = " " + data.datetime
      date_element.classList.add("date")
      date_element.style.display = "inline"
      date_element.innerHTML += "<br>"
      let new_message = document.createElement('div')
      new_message.classList.add("message")
      new_message.classList.add("list-group-item")
      new_message.id = data.id
      new_message.innerText = data.message
      new_message.prepend(date_element)
      new_message.prepend(username_element)
      document.getElementById('messages').insertBefore(new_message, document.getElementById('messages').firstChild)
      let button = document.getElementById('no-more')
      button.parentNode.insertBefore(button, document.getElementById('messages').firstChild);

      var converter = new showdown.Converter();
      document.getElementById(new_message.id).innerHTML = converter.makeHtml(document.getElementById(new_message.id).innerHTML);
      document.getElementById(new_message.id).lastChild.style.display = 'inline';
      if (data.mine) {
        document.getElementById(new_message.id).classList.add("mine")
        if (!data.deleted) {
          document.getElementById(new_message.id).children[0].innerHTML += "<button type=\"button\" class=\"btn-close position-absolute end-0 me-2 delete-message\" alt=\"Delete Note\"></button>"
          document.getElementById(data.id).children[0].lastChild.addEventListener('click', function() {
            deleteMessage(data.id);
          });
        }
      }
    });
    if (lastScrollTop == 0) {
      var scrollDiff = el.scrollHeight - lastScrollHeight;
      el.scrollTop += scrollDiff; 
    }
    messages_loaded += 100
    getting_more = false;
})});