from flask import Flask, request, render_template, url_for, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
from inference_sdk import InferenceHTTPClient
from datetime import datetime
from chatbot import chatbot

# Initialize Flask App
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Initialize RoboFlow Clients
PNEUMONIA_CLIENT = InferenceHTTPClient(
  api_url=os.getenv("ROBOFLOW_API_URL"),
  api_key=os.getenv("ROBOFLOW_API_KEY")
)
PNEUMONIA_MODEL_ID = "pneumonia-itjkr/2"  # Update this with your exact model version

TB_CLIENT = InferenceHTTPClient(
  api_url="https://detect.roboflow.com",
  api_key="hjCFUfsJBCSxi8KzP8yC"
)
TB_MODEL_ID = "tb-detection-227v0/1"

FRACTURE_CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="hjCFUfsJBCSxi8KzP8yC"
)
FRACTURE_MODEL_ID = "fracture-ov5p1/1"

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
  if 'file' not in request.files:
      return "No file part"
  file = request.files['file']
  selected_model = request.form.get('selected-model', 'pneumonia')
  if file.filename == '':
      return "No selected file"
  if file:
      filepath = os.path.join(UPLOAD_FOLDER, file.filename)
      file.save(filepath)

      # Make prediction with selected model
      if selected_model == 'pneumonia':
          result = PNEUMONIA_CLIENT.infer(filepath, model_id=PNEUMONIA_MODEL_ID)
      elif selected_model == 'tuberculosis':
          result = TB_CLIENT.infer(filepath, model_id=TB_MODEL_ID)
      else:  # fracture
          result = FRACTURE_CLIENT.infer(filepath, model_id=FRACTURE_MODEL_ID)
      
      predictions = result["predictions"]
      
      # Draw predictions on the image
      result_image_path = draw_predictions(filepath, predictions)

      return render_template(
          'result.html', 
          original_image=url_for('static', filename=f'uploads/{file.filename}'),
          result_image=url_for('static', filename=f'results/{os.path.basename(result_image_path)}'),
          predictions=predictions,
          selected_model=selected_model
      )

def draw_predictions(image_path, predictions):
  image = Image.open(image_path)
  draw = ImageDraw.Draw(image)
  font = ImageFont.load_default()

  for pred in predictions:
      x, y, width, height = pred["x"], pred["y"], pred["width"], pred["height"]
      confidence = pred["confidence"]
      label = pred["class"]

      # Calculate bounding box
      left = x - width / 2
      top = y - height / 2
      right = x + width / 2
      bottom = y + height / 2

      # Draw bounding box
      draw.rectangle([left, top, right, bottom], outline="red", width=3)

      # Add label and confidence
      text = f"{label}: {confidence:.2%}"
      draw.text((left, top - 10), text, fill="red", font=font)

  # Save result
  result_image_path = os.path.join(RESULT_FOLDER, os.path.basename(image_path))
  image.save(result_image_path)
  return result_image_path

@app.route('/ask_chatgpt', methods=['POST'])
def ask_chatgpt():
  question = request.form['question']
  prediction = request.form['prediction']
  confidence = request.form['confidence']
  selected_model = request.form['selected_model']
  
  context = f"The user's scan has been analyzed for {selected_model}, and the prediction is {prediction} with a confidence of {confidence}%. "
  
  if chatbot is None:
      return jsonify({'answer': "Sorry, the chatbot is currently unavailable. Please try again later."})
  
  try:
      response = chatbot.get_response(context, question)
      return jsonify({'answer': response})
  except Exception as e:
      app.logger.error(f"Error in ask_chatgpt: {str(e)}")
      return jsonify({'answer': "I'm sorry, but I encountered an error while processing your request. Please try again later."})

@app.route('/parkinsons_test')
def parkinsons_test():
    return render_template('parkinsons_test.html')

@app.route('/get_pattern', methods=['GET'])
def get_pattern():
    pattern = get_random_pattern()
    return jsonify(pattern)

@app.route('/analyze_tracing', methods=['POST'])
def analyze_tracing_route():
    data = request.json
    user_path = data['user_path']
    original_path = data['original_path']
    result = analyze_tracing(user_path, original_path)
    return jsonify(result)

if __name__ == '__main__':
  app.run(debug=True)