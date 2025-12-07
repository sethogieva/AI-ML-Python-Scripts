from flask import Flask, request, jsonify, render_template_string
import joblib
import numpy as np
import os
from PIL import Image

try:
        import torch
        import torch.nn.functional as F
        from torchvision import transforms, models
except Exception:
        torch = None

app = Flask(__name__)

# Numeric model (scikit-learn)
NUMERIC_MODEL_PATH = os.path.join("AI & ML Models", "iris_model.pkl")
numeric_model = None
if os.path.exists(NUMERIC_MODEL_PATH):
        try:
                numeric_model = joblib.load(NUMERIC_MODEL_PATH)
        except Exception:
                numeric_model = None

# Image model (PyTorch) - optional, saved by training script
IMAGE_MODEL_DIR = os.path.join("Flower Recognition Model")
IMAGE_MODEL_PATH = os.path.join(IMAGE_MODEL_DIR, "image_model.pth")
IMAGE_CLASSES_PATH = os.path.join(IMAGE_MODEL_DIR, "classes.json")
image_model = None
image_classes = None
device = 'cpu'

def load_image_model():
        global image_model, image_classes, device
        if torch is None:
                return
        if not os.path.exists(IMAGE_MODEL_PATH) or not os.path.exists(IMAGE_CLASSES_PATH):
                return
        import json
        with open(IMAGE_CLASSES_PATH, 'r') as f:
                image_classes = json.load(f)
        num_classes = len(image_classes)
        model = models.resnet18(pretrained=False)
        model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
        state = torch.load(IMAGE_MODEL_PATH, map_location='cpu')
        model.load_state_dict(state)
        model.eval()
        image_model = model

load_image_model()

SPECIES = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}

INDEX_HTML = '''
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Flower Recognizer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f7fafc; }
            .card { border-radius: 12px; box-shadow: 0 6px 18px rgba(35,44,70,0.08); }
            .upload-area { border: 2px dashed #e2e8f0; border-radius: 8px; padding: 1rem; text-align:center; background:#fff }
            .preview { max-width:100%; height:auto; display:block; margin:0 auto }
            .muted { color:#6b7280 }
            .result { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
            .species { font-size: 1.5rem; font-weight: 600 }
            .confidence { font-size: 1.1rem; color:#475569 }
            .color-swatch { width:36px; height:36px; border-radius:6px; display:inline-block; vertical-align:middle; margin-left:8px; border:1px solid #e2e8f0 }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-10">
                    <div class="card p-4">
                        <div class="row g-4">
                            <div class="col-md-6">
                                <h2 class="mb-3">Flower Recognizer</h2>
                                <p class="muted">Upload a photo of a flower or enter measurements to get a prediction.</p>

                                <div class="mb-3">
                                    <label class="form-label">Enter measurements (optional)</label>
                                    <div class="input-group mb-2">
                                        <input class="form-control" id="slen" placeholder="sepal length" value="5.1">
                                        <input class="form-control" id="swid" placeholder="sepal width" value="3.5">
                                    </div>
                                    <div class="input-group">
                                        <input class="form-control" id="plen" placeholder="petal length" value="1.4">
                                        <input class="form-control" id="pwid" placeholder="petal width" value="0.2">
                                    </div>
                                    <button id="predict-numeric" class="btn btn-primary mt-3">Predict from numbers</button>
                                </div>

                                <hr>

                                <label class="form-label">Or upload an image</label>
                                <div class="upload-area mb-3" id="dropzone">
                                    <div class="mb-2">Drag & drop an image here, or</div>
                                    <input class="form-control" type="file" id="image-file" accept="image/*">
                                    <img id="preview" class="preview mt-3" style="display:none">
                                </div>
                                <button id="predict-image" class="btn btn-success">Predict from image</button>

                                <div class="mt-4">
                                    <h6>Health</h6>
                                    <a href="/health">/health</a>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <h5>Result</h5>
                                <div id="result" class="result p-3 bg-white" style="min-height:220px;border-radius:8px;border:1px solid #eef2f7">(no result yet)</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
        const preview = document.getElementById('preview');
        const fileInput = document.getElementById('image-file');
        const dropzone = document.getElementById('dropzone');

        fileInput.addEventListener('change', () => { showPreview(fileInput.files[0]); });
        dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.borderColor='#93c5fd'; });
        dropzone.addEventListener('dragleave', () => { dropzone.style.borderColor=''; });
        dropzone.addEventListener('drop', (e) => { e.preventDefault(); fileInput.files = e.dataTransfer.files; showPreview(fileInput.files[0]); dropzone.style.borderColor=''; });

        function showPreview(file){ if(!file) return; const url = URL.createObjectURL(file); preview.src = url; preview.style.display = 'block'; }

                function renderResult(obj){
                        const out = document.getElementById('result');
                        out.innerHTML = '';
                        if(obj.error){
                                out.innerHTML = `<div class=\"alert alert-danger\">Error: ${obj.error}</div>`;
                                return;
                        }

                        // Common display pieces
                        const name = obj.prediction_name || (obj.prediction_index !== undefined ? ('Class ' + obj.prediction_index) : 'Unknown');
                        const confidence = Math.round((obj.confidence||0)*100);
                        const avg = obj.avg_color_rgb || null;
                        const method = obj.method || 'numeric';

                        // Build card
                        const card = document.createElement('div');
                        card.className = 'p-3 bg-white';
                        card.style.borderRadius = '8px';
                        card.style.border = '1px solid #eef2f7';

                        const title = document.createElement('div');
                        title.className = 'd-flex align-items-center';
                        title.innerHTML = `<div style=\"flex:1\"><div class=\\"species\\">${name}</div><div class=\\"confidence\\">Confidence: ${confidence}%</div></div>`;

                        if(avg){
                                const sw = document.createElement('div');
                                sw.className = 'color-swatch';
                                const r = Math.round(avg[0]*255), g = Math.round(avg[1]*255), b = Math.round(avg[2]*255);
                                sw.style.background = `rgb(${r}, ${g}, ${b})`;
                                title.appendChild(sw);
                        }

                        card.appendChild(title);

                        // Method / explanation
                        const explain = document.createElement('div');
                        explain.style.marginTop = '8px';
                        explain.className = 'muted';
                        if(method === 'image-model'){
                                explain.textContent = 'Predicted by the trained image model.';
                        } else if(method === 'visual-heuristic-placeholder'){
                                explain.textContent = 'Predicted by a simple visual heuristic (low confidence). Consider training the image model for better results.';
                        } else if(method === 'numeric'){
                                explain.textContent = 'Predicted by numeric measurements.';
                        } else {
                                explain.textContent = `Method: ${method}`;
                        }
                        card.appendChild(explain);

                        // Nice confidence bar
                        const barWrap = document.createElement('div');
                        barWrap.style.marginTop = '12px';
                        barWrap.innerHTML = `
                                <div style=\"background:#eef2f7;border-radius:8px;height:12px;width:100%\">\
                                        <div style=\"height:12px;border-radius:8px;background:linear-gradient(90deg,#10b981,#3b82f6);width:${confidence}%\"></div>\
                                </div>\
                                <div style=\"font-size:0.85rem;color:#6b7280;margin-top:6px\">Confidence: ${confidence}%</div>`;
                        card.appendChild(barWrap);

                        // Extra details (toggle)
                        const details = document.createElement('details');
                        details.style.marginTop = '10px';
                        details.innerHTML = '<summary style=\"cursor:pointer;color:#475569\">Details</summary>';
                        const pre = document.createElement('pre');
                        pre.style.background = '#f8fafc';
                        pre.style.padding = '8px';
                        pre.style.borderRadius = '6px';
                        pre.textContent = JSON.stringify(obj, null, 2);
                        details.appendChild(pre);
                        card.appendChild(details);

                        out.appendChild(card);
                }

        document.getElementById('predict-numeric').addEventListener('click', async ()=>{
            const payload = { input: [parseFloat(slen.value), parseFloat(swid.value), parseFloat(plen.value), parseFloat(pwid.value)] };
            const res = await fetch('/predict', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            const j = await res.json(); renderResult(j);
        });

        document.getElementById('predict-image').addEventListener('click', async ()=>{
            if(!fileInput.files[0]){ alert('Please choose an image first'); return; }
            const fd = new FormData(); fd.append('file', fileInput.files[0]);
            document.getElementById('result').textContent = 'Analyzing image...';
            const res = await fetch('/predict-image', { method:'POST', body: fd });
            const j = await res.json(); renderResult(j);
        });
        </script>
    </body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
        return render_template_string(INDEX_HTML)


@app.route('/health', methods=['GET'])
def health():
        return jsonify({'status': 'ok'}), 200


@app.route('/predict', methods=['POST'])
def predict():
        if numeric_model is None:
                return jsonify({'error': 'numeric model not available'}), 500
        data = request.get_json(force=True)
        input_arr = np.array(data['input']).reshape(1, -1)
        pred_index = int(numeric_model.predict(input_arr)[0])
        pred_name = SPECIES.get(pred_index, str(pred_index))
        return jsonify({'prediction_index': pred_index, 'prediction_name': pred_name})


@app.route('/predict-image', methods=['POST'])
def predict_image():
        # Accepts multipart/form-data with file field named 'file'
        if 'file' not in request.files:
                return jsonify({'error': 'no file uploaded'}), 400
        f = request.files['file']
        try:
                img = Image.open(f.stream).convert('RGB')
        except Exception as e:
                return jsonify({'error': 'cannot open image', 'detail': str(e)}), 400

        # Compute average color
        arr = np.array(img.resize((64,64))) / 255.0
        avg = arr.mean(axis=(0,1))
        r,g,b = avg.tolist()

        # If a trained image model exists, use it
        if image_model is not None:
                if torch is None:
                        return jsonify({'error': 'torch not available on server'}), 500
                preprocess = transforms.Compose([
                        transforms.Resize(256),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                ])
                input_tensor = preprocess(img).unsqueeze(0)  # shape 1,C,H,W
                with torch.no_grad():
                        outputs = image_model(input_tensor)
                        probs = F.softmax(outputs, dim=1).cpu().numpy()[0]
                        top_idx = int(probs.argmax())
                        top_conf = float(probs[top_idx])
                        top_name = image_classes[top_idx] if image_classes else str(top_idx)
                return jsonify({
                        'method': 'image-model',
                        'prediction_name': top_name,
                        'confidence': round(top_conf, 3),
                        'avg_color_rgb': [round(float(x),3) for x in (r,g,b)]
                })

        # Fallback: simple visual heuristic (if no image model)
        if g > r and g > b and g > 0.38:
                guess = 'setosa'
                conf = 0.45 + (g - 0.38)
        elif r > g and r > b and r > 0.35:
                guess = 'versicolor'
                conf = 0.40 + (r - 0.35)
        else:
                guess = 'virginica'
                conf = 0.35 + max(r,g,b) - 0.3
        conf = float(min(max(conf, 0.0), 0.99))
        return jsonify({
                'method': 'visual-heuristic-placeholder',
                'prediction_name': guess,
                'confidence': round(conf, 3),
                'avg_color_rgb': [round(float(x),3) for x in (r,g,b)]
        })


if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80)
