function deleteNote(noteId) {
    fetch('api/delete-note', {
        method: 'POST',
        body: JSON.stringify({ note_id: noteId }),
    }).then((_res) => {
        document.location = document.URL;
    });
}

function editNote(noteId) {
    console.log(document.querySelector("#note-" + noteId));
}
