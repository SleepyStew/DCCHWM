function deleteNote(noteId) {
    axios.post('api/delete-note', {
        note_id: noteId
    }).then((_res) => {
        document.location = document.URL;
    });
}

function updateHeight(el) {
    el.style.height = "unset";
    el.style.height = el.scrollHeight + 2 + "px";
}

function editNote(noteId) {
    let note = document.querySelector("#note-" + noteId);
    let unformatted_note = document.querySelector("#note-plain-" + noteId);
    
    let editbox = document.createElement("textarea");
    editbox.classList.add("form-control");

    editbox.innerHTML = unformatted_note.textContent.trim();
    editbox.id = noteId + "-edit";
    editbox.maxLength = 1024;

    editbox.addEventListener("input", (event) => {
        updateHeight(event.target);
    })

    let savebutton = document.createElement("button");
    savebutton.classList.add("btn");
    savebutton.classList.add("btn-primary");
    savebutton.classList.add("mt-2");
    savebutton.classList.add("me-2");
    savebutton.style.maxWidth = "150px"
    savebutton.innerText = "Save Note";
    savebutton.id = noteId + "-edit-button";
    savebutton.addEventListener('click', () => { saveEdited(event) });

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
    updateHeight(editbox);

    note.style.display = "none";
}

function saveEdited(event) {
    let noteId = event.target.id.split("-")[0];
    let content = event.target.previousSibling.value;
    axios.post('api/edit-note', {
        note_id: noteId,
        note_content: content
    }).then((_res) => {
        document.location = document.URL;
    });
}

function cancelEdit(noteId) {
    document.getElementById(noteId + "-edit-button").remove();
    document.getElementById(noteId + "-cancel-button").remove();
    document.getElementById("note-" + noteId).style.display = "block";
    document.getElementById(noteId + "-edit").remove()
}

window.addEventListener("load", () => {
    document.querySelector("#note").addEventListener("input", (event) => {
        updateHeight(event.target);
    })
})
