document.addEventListener('DOMContentLoaded', function() {
    const mainContentTextarea = document.getElementById('main_content');
    const preMediaContentTextarea = document.getElementById('pre_media_content');
    const mainPreviewDiv = document.getElementById('main_preview');
    const preMediaPreviewDiv = document.getElementById('pre_media_preview');

    if ((mainContentTextarea && mainPreviewDiv) || (preMediaContentTextarea && preMediaPreviewDiv)) {
        let debounceTimer;
        function reloadPreview(contentType, disableDebounce=false) {
            function inner() {
                const content = contentType === 'main' ? mainContentTextarea.value : preMediaContentTextarea.value;
                const previewDiv = contentType === 'main' ? mainPreviewDiv : preMediaPreviewDiv;
                
                fetch('/preview', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'content': content,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    previewDiv.innerHTML = data.html;
                })
                .catch(error => console.error('Error:', error));
            }
            if (disableDebounce) {
                inner();
            } else {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(inner, 300);    
            }
        }

        if (mainContentTextarea) {
            mainContentTextarea.addEventListener('input', () => reloadPreview('main'));
            preMediaContentTextarea.addEventListener('input', () => reloadPreview('pre_media'));
            reloadPreview('main', true);
            reloadPreview('pre_media', true);

        }
    }
});