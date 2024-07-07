from flask import Flask, request, render_template, stream_with_context
from discussionclub import yeld_rounds
from threading import Semaphore
from flask.logging import default_handler
import logging

app = Flask(__name__)

for logger in (
    logging.getLogger('discussionclub'),
    logging.getLogger('launchollamakaggle'),
):
    logger.addHandler(default_handler)

@app.route('/')
def index():
    return render_template('index.html')

generate_lock = Semaphore(1)

def get_ip_addr():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy

@app.route('/discuss', methods=['post'])
def discuss():
    topic = request.form['topic']
    def generate():
        if not generate_lock.acquire(False):
            yield "Another session running. Try again later\n"
            return
        else:
            try:
                try:
                    new_part = False
                    for part in yeld_rounds(topic=topic, rounds=3):
                        if 'BOT' in part or 'SYSTEM:' in part or 'MODERATOR:' in part:
                            yield f'<h3 class="botheader">{part}</h3>'
                        else:
                            for x in part.split('\n'):
                                yield x
                except Exception as e:
                    app.logger.error(f"Error during generation: {e}")
                    yield f'<h3 class="botheader">SYSTEM: Error during generation: {e}</h3>'
            finally:
                generate_lock.release()

    app.logger.info(f"Starting discussion from {get_ip_addr()} on {topic}")
    response = app.response_class(stream_with_context(generate()), mimetype='text/html')
    # special header for pythonanywhere to stream the response instead of buffering 
    response.headers['X-Accel-Buffering'] = 'no'
    return response

if __name__ == '__main__':
    app.run(debug=True)
