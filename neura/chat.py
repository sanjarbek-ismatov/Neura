import functools
from flask import (
    Blueprint, flash, g, get_flashed_messages, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions

from uuid import uuid4
from neura.db import get_db

chat = Blueprint('chat', __name__, url_prefix='/chat')




@chat.route('/new') # it is like creating room
def create_chat():
    db = get_db()
    id = f'{uuid4()}'
    db.execute("INSERT INTO chat (id, summary_title, owner) VALUES (?, ?, ?)", (id, "Empty chat", session.get('user_id')))
    db.commit()
    
    return redirect(url_for('chat.chat_view', chat_id=id))
@chat.route('/<chat_id>',methods=('GET', 'POST'))
def chat_view(chat_id):
    db = get_db()

    check_url = db.execute("SELECT EXISTS(SELECT 1 FROM chat WHERE id = ?)", (chat_id, )).fetchone()[0]
    
    if not check_url:
        raise OSError()
    
    if not db.execute('SELECT * FROM chat WHERE id = ?', (chat_id, )).fetchone()['owner'] == session.get('user_id'):
        return exceptions.Forbidden()
    

    if request.method == 'POST':
        user_query = request.form['query']
        

        db.execute('INSERT INTO query (msg, owner, chat) VALUES (?, ?, ?)', (user_query, session.get('user_id'), chat_id))
        db.commit()
    

    queries = db.execute('SELECT * FROM query WHERE chat = ?', (chat_id, )).fetchall()

    return render_template('chat/chat_home.html', chat_id=chat_id, queries=queries)
def get_my_history():
    db = get_db()
    return db.execute("SELECT * FROM chat WHERE owner = ?", (session.get('user_id'), ))


@chat.route('/<chat_id>/delete', methods=['POST', 'GET'])
def delete_chat(chat_id):
    db = get_db()
    check_url = db.execute("SELECT EXISTS(SELECT 1 FROM chat WHERE id = ?)", (chat_id, )).fetchone()[0]
    if not check_url:
        return exceptions.NotFound()
    if not db.execute('SELECT * FROM chat WHERE id = ?', (chat_id, )).fetchone()['owner'] == session.get('user_id'):
        return exceptions.Forbidden()
    
    db.execute('DELETE FROM chat WHERE id = ?', (chat_id, ))
    db.commit()
    flash('Chat has been deleted', 'success')
    return redirect(url_for('home'))
