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
    
    note.parentNode.insertBefore(editbox, note.nextSibling);

    note.style.display = "none";
}
