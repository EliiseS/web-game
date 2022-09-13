from flask import Flask, render_template, redirect, request, flash, session, Markup, Response
from src.in_memory_storage import InMemoryStorage, StorageItem

app = Flask(__name__)
app.secret_key = "f3cfe9ed8fae309f02079dbf"  # random string

database = InMemoryStorage()
APP_VERSION = '0.0.1'


@app.context_processor
def inject_app_version():
    return dict(app_version=APP_VERSION)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/words')
def words():
    return render_template('words.html')


@app.route('/upload_word', methods=['POST'])
def upload_word():
    secret_word = request.form['secretWord']
    # 'image' is the name of the input in HTML
    image_file = request.files['image']

    image_bytes = image_file.stream.read()  # actual image content
    # mime type, e.g. image/png, image/jpeg
    image_content_type = image_file.content_type

    database.add(StorageItem(
        image_bytes=image_bytes,
        image_content_type=image_content_type,
        secret_word=secret_word,
    ))

    flash("Uploaded word " + repr(secret_word))
    # display all words saved so far
    flash("All available words: " + repr(database.get_all_secrets()))

    flash('Uploaded %s bytes of type %s' %
          (len(image_bytes), image_content_type))
    return redirect('/')


@app.route('/game', methods=['GET'])
def game():
    if database.is_empty():
        flash("No images uploaded yet! Please upload at least one image to start guessing")
        return redirect("/")

    if 'secret_word_id' in session:
        if database.has_index(session['secret_word_id']):
            return render_template('game.html')

    word_id = database.get_random_item_index()
    if word_id is None:
        flash("No words uploaded yet! Please upload at least one word to start guessing")
        return redirect("/")

    session['secret_word_id'] = word_id

    return render_template('game.html')


@ app.route('/make_a_guess', methods=['POST'])
def make_a_guess():
    if 'secret_word_id' not in session:  # this should never happen
        flash("You can't guess words without starting the game first!")
        return redirect('/game')

    item = database.get_item_by_index(session['secret_word_id'])

    if request.form['guessed_word'] == item.secret_word:
        flash(Markup(
            "You guessed right! Good job! The secret word was <b>%s</b>" % item.secret_word))
        del session['secret_word_id']
        return redirect('/')

    flash("You didn't guess right! Try again!")
    return redirect('/game')


@app.route('/image', methods=['GET'])
def get_image():
    item_id = int(request.args['item_id'])
    item = database.get_item_by_index(item_id)
    return Response(item.image_bytes, mimetype=item.image_content_type)
