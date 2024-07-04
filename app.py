from flask import Flask, request, render_template
from discussionclub import yeld_rounds

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/discuss', methods=['post'])
def discuss():
    topic = request.form['topic']
    def generate():
        new_part = False
        yield '<p class="bottext">'
        for part in yeld_rounds(topic=topic, rounds=3):
            if 'BOT' in part or 'Starting discussion' in part:
                yield f'<h3 class="botheader">{part}</h3>'
            else:
                for x in part.split('\n'):
                    yield x
        yield "</p>"
    app.logger.info(topic)
    return app.response_class(generate(), mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
