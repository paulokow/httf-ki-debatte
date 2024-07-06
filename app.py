from flask import Flask, request, render_template, stream_with_context
from discussionclub import yeld_rounds

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

generate_lock = False

@app.route('/discuss', methods=['post'])
def discuss():
    topic = request.form['topic']
    def generate():
        if generate_lock:
            generate_lock = True
            yield "Another session running. Try again later\n"
            return
        else:
            try:
                new_part = False
                for part in yeld_rounds(topic=topic, rounds=3):
                    if 'BOT' in part or 'SYSTEM:' in part or 'MODERATOR:' in part:
                        yield f'<h3 class="botheader">{part}</h3>'
                    else:
                        for x in part.split('\n'):
                            yield x
            finally:
                generate_lock = False
    app.logger.info(topic)
    return app.response_class(stream_with_context(generate()), mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
