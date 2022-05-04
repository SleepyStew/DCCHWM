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
    editbox.innerText = note.textContent.trim();
    editbox.id = noteId + "-edit";

    let savebutton = document.createElement("button");
    savebutton.classList.add("btn");
    savebutton.classList.add("btn-primary");
    savebutton.innerText = "Save Note";
    savebutton.onclick = "saveEdited(" + noteId + ")"
    
    note.parentNode.insertBefore(savebutton, note.nextSibling);
    note.parentNode.insertBefore(editbox, note.nextSibling);

    note.style.display = "none";
}

function saveEdited(noteId) {
    console.log(noteId);
}
