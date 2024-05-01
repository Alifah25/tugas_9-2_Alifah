from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    jsonify
)
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

password = 'sparta'
cxn_str = f'mongodb+srv://Alifah:{password}@cluster0.lh6vlnc.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cxn_str)

db = client.dbsparta_plus_week2

def get_suggested_words():
    suggested_words = ["description", "sun", "pride", "father", "banana", "pink",
    "wow", "candle", "you", "wine", "plastic", "sense", "day", "million", "phone",
    "skip", "key", "small", "card", "bug", "hey", "silver", "owl", "roundabout",
    "cash", "test", "master", "cry", "artifact", "cup", "tail", "shit"]
    return suggested_words

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    msg = request.args.get('msg')
    return render_template('index.html', words=words, msg=msg)

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = "ab47db79-3ddd-454a-b89e-bc53de716ac2"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'error',
            msg=f'Could not find the word, {keyword}'
        ))

    if type(definitions[0]) is str:
        suggestions = ', '.join(definitions)
        return redirect(url_for(
            'error',
            msg=f'Could not find the word, {keyword}, did you mean one of these words: {suggestions}'
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d')
    }
    db.words.insert_one(doc)

    return jsonify({
        'result' : 'success',
        'msg' : f'the word, {word}, was saved!!',
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    db.examples.delete_many({'word': word})

    return jsonify({
        'result' : 'success',
        'msg' : f'the word, {word}, was delete',
    })

@app.route('/error')
def error():
    msg = request.args.get('msg')
    suggested_words = get_suggested_words()
    return render_template('error.html', msg=msg, suggested_words=suggested_words)

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word': word})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id')),
        })
    return jsonify({
        'result': 'success',
        'examples': examples
    })

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word': word,
        'example': example,
    }
    db.examples.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'Your example, {example}, for the word, {word}, was saved!',
    })

@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})
    return jsonify({
        'result': 'success',
        'msg': f'Your example for the word, {word}, was deleted!',
    })

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
