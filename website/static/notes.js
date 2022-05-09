function deleteNote(noteId) {
    fetch('api/delete-note', {
        method: 'POST',
        body: JSON.stringify({ note_id: noteId }),
    }).then((_res) => {
        document.location = document.URL;
    });
}

function editNote(noteId) {
    let note = document.querySelector("#note-" + noteId);
    
    let editbox = document.createElement("textarea");
    editbox.classList.add("form-control");

    editbox.innerHTML = note.textContent.trim();
    editbox.id = noteId + "-edit";
    editbox.maxlength = 256;

    let savebutton = document.createElement("button");
    savebutton.classList.add("btn");
    savebutton.classList.add("btn-primary");
    savebutton.classList.add("mt-2");
    savebutton.classList.add("me-2");
    savebutton.style.maxWidth = "150px"
    savebutton.innerText = "Save Note";
    savebutton.id = noteId + "-edit-button";
    savebutton.onclick = saveEdited;

    let cancelbutton = document.createElement("button");
    cancelbutton.classList.add("btn");
    cancelbutton.classList.add("btn-danger");
    cancelbutton.classList.add("mt-2");
    cancelbutton.style.maxWidth = "150px"
    cancelbutton.innerText = "Cancel";
    cancelbutton.id = noteId + "-cancel-button";
    cancelbutton.addEventListener('click', () => { cancelEdit(noteId) });
    
    note.parentNode.insertBefore(cancelbutton, note.nextSibling);
    note.parentNode.insertBefore(savebutton, note.nextSibling);
    note.parentNode.insertBefore(editbox, note.nextSibling);

    note.style.display = "none";
}

function saveEdited(event) {
    let noteId = event.target.id.split("-")[0];
    let content = event.target.previousSibling.value;
    fetch('api/edit-note', {
        method: 'POST',
        body: JSON.stringify({ note_id: noteId, note_content: content }),
    }).then((_res) => {
        document.location = document.URL;
    });
}

function cancelEdit(noteId) {
    console.log(noteId);
    document.getElementById(noteId + "-edit-button").remove();
    document.getElementById(noteId + "-cancel-button").remove();
    document.getElementById("note-" + noteId).style.display = "block";
    document.getElementById(noteId + "-edit").remove()
}
