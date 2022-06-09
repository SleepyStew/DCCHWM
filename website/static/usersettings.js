const editor = monaco.editor.create(document.getElementById('custom-js'), {
    value: document.getElementById('custom-javascript-default').innerText,
	language: 'javascript',
    theme: 'vs-dark'
});

function submit_custom_js() {
    document.getElementById('custom-js-field').value = document.getElementsByClassName("view-lines")[0].innerText;
    document.getElementById('custom-js-form').submit();
}