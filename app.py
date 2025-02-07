from flask import Flask, request, jsonify
import os
import json
from datetime import datetime, UTC

app = Flask(__name__, static_url_path='')

NOTES_DIR = 'notes'
if not os.path.exists(NOTES_DIR):
   os.makedirs(NOTES_DIR)

def get_next_id():
   existing_ids = [int(f.split('.')[0]) for f in os.listdir(NOTES_DIR) if f.endswith('.json')]
   return max(existing_ids, default=0) + 1

@app.route('/')
def serve_static():
   return app.send_static_file('index.html')

@app.route('/api/notes', methods=['GET'])
def get_notes():
   notes = []
   for filename in os.listdir(NOTES_DIR):
       if filename.endswith('.json'):
           with open(os.path.join(NOTES_DIR, filename)) as f:
               note = json.load(f)
               notes.append(note)
   return jsonify(sorted(notes, key=lambda x: x['created_at'], reverse=True))

@app.route('/api/notes', methods=['POST'])
def create_note():
   data = request.get_json()
   note_id = get_next_id()
   note = {
       'id': note_id,
       'title': data['title'],
       'content': data['content'],
       'created_at': datetime.now(UTC).isoformat()
   }
   with open(os.path.join(NOTES_DIR, f'{note_id}.json'), 'w') as f:
       json.dump(note, f)
   return jsonify(note)

@app.route('/api/notes/<int:id>', methods=['PUT'])
def update_note(id):
   filepath = os.path.join(NOTES_DIR, f'{id}.json')
   if not os.path.exists(filepath):
       return '', 404
       
   with open(filepath) as f:
       note = json.load(f)
   
   data = request.get_json()
   note['title'] = data['title']
   note['content'] = data['content']
   
   with open(filepath, 'w') as f:
       json.dump(note, f)
   return jsonify(note)

@app.route('/api/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
   filepath = os.path.join(NOTES_DIR, f'{id}.json')
   if os.path.exists(filepath):
       os.remove(filepath)
   return '', 204

if __name__ == '__main__':
   app.run(debug=True, port=5000)