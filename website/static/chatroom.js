import { io } from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js";

const socket = io.connect('http://127.0.0.1:30015/');

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