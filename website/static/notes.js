function deleteNote(noteId) {
    fetch('api/delete-note', {
        method: 'POST',
        body: JSON.stringify({ note_id: noteId }),
    }).then((_res) => {
        location.reload();
    });
}