window.submit_custom_js = function submit_custom_js() {
    document.getElementById('custom-js-field').value = document.getElementsByClassName("view-lines")[0].innerText.replace(/\s/g, ' ');
    document.getElementById('custom-js-form').submit();
}

window.addEventListener("load", function(){
    const editor = monaco.editor.create(document.getElementById('custom-js'), {
        value: document.getElementById('custom-javascript-default').innerText,
        language: 'javascript',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: {
            enabled: false
        }
    });
});
