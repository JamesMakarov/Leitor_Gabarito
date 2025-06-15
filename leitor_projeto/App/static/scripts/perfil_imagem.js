let cropper;
                const inputFoto = document.getElementById('inputFoto');
                const cropperImagem = document.getElementById('cropperImagem');
                const fotoCropada = document.getElementById('fotoCropada');

                inputFoto.addEventListener('change', function () {
                  const file = this.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                      cropperImagem.src = e.target.result;
                      cropperImagem.style.display = 'block';

                      if (cropper) cropper.destroy();
                      cropper = new Cropper(cropperImagem, {
                        aspectRatio: 1,
                        viewMode: 1,
                        autoCropArea: 1,
                        movable: true,
                        zoomable: true,
                        scalable: false,
                        rotatable: false,
                      });
                    };
                    reader.readAsDataURL(file);
                  }
                });

                document.querySelector('form').addEventListener('submit', function (e) {
                  if (cropper) {
                    e.preventDefault(); // Impede envio imediato

                    cropper.getCroppedCanvas({
                      width: 400,
                      height: 400
                    }).toBlob(function (blob) {
                      const reader = new FileReader();
                      reader.onloadend = function () {
                        fotoCropada.value = reader.result; // Base64 da imagem cropada
                        e.target.submit(); // Agora sim envia
                      };
                      reader.readAsDataURL(blob);
                    }, 'image/jpeg');
                  }
                });