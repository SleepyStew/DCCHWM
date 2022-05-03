function deleteNote(noteId) {
    fetch('/delete-note/', {
        method: 'POST',
        body: JSON.stringify({ note_id: noteId }),
    }).then((_res) => {
        window.location.reload();
    });
}