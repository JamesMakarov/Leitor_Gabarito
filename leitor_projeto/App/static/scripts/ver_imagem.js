const input = document.getElementById('inputFoto');
              const preview = document.getElementById('previewFoto');
              input.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = function (e) {
                    preview.setAttribute('src', e.target.result);
                    preview.style.display = 'inline-block';
                  };
                  reader.readAsDataURL(file);
                }
              });