const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const captureButton = document.getElementById("captureButton");
const result = document.getElementById("result");

navigator.mediaDevices
    .getUserMedia({
        video: {
            facingMode: "environment"
        },
        audio: false
    })
    .then(function (stream) {
        video.srcObject = stream;
    })
    .catch(function (error) {
        console.error("Camera error:", error);
        result.innerHTML = "Camera permission denied or camera unavailable.";
    });


captureButton.addEventListener("click", async function () {

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    canvas.toBlob(async function (blob) {

        const formData = new FormData();

        formData.append(
            "image",
            blob,
            "animal.jpg"
        );

        result.innerHTML = "Scanning animal...";

        try {

            const response = await fetch("/api/scan", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {

                result.innerHTML = `
                    <h2>✅ Animal Image Received</h2>
                    <p>${data.message}</p>
                    <p>Image: ${data.filename}</p>
                `;

            } else {

                result.innerHTML = `
                    <p>❌ ${data.message}</p>
                `;
            }

        } catch (error) {

            console.error(error);

            result.innerHTML = `
                <p>❌ Could not connect to Flask.</p>
            `;
        }

    }, "image/jpeg");

});