#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template, request, redirect, session, g, flash, url_for
import sqlite3
import validators
import os
import requests

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'bookcatalogue.db'),
    SECRET_KEY='secret key'
    ))


# In[ ]:


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# In[ ]:


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# In[ ]:


@app.route('/')
def hello_world():
    return redirect('/login')


# In[ ]:


# User must log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select id from users where username=? and password=?', [request.form['username'], request.form['password']])
        validUser = cur.fetchone()
        if validUser:
            session['logged_in'] = True
            session['user_id'] = validUser[0]
            flash('You are logged in')
            return redirect(url_for('show_books'))
        else:
            session['logged_in'] = False
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


# In[ ]:


@app.route('/showbooks', methods=['GET'])
def show_books():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    db = get_db()
    cur = db.execute('select user_id, title, author, page_count, average_rating, thumbnail from bookcatalogue where user_id=?', [session['user_id']])
    books = cur.fetchall()
    return render_template('showbooks.html', books=books)


# In[ ]:


@app.route('/searchbooks', methods=['GET', 'POST'])
def search_books():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        # check google for search results
        r = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:' + request.form['isbnnumber'])
        json = r.json()
        searchresults = []
        for item in json['items']:
            result = {}
            result['title'] = item['volumeInfo']['title']
            # check for authors
            if 'authors' in item['volumeInfo'].keys():
                result['author'] = item['volumeInfo']['authors'][0]
            else:
                result['author'] = 'Author not found'
            # check for pageCount
            if 'pageCount' in item['volumeInfo'].keys():
                result['pageCount'] = item['volumeInfo']['pageCount']
            else:
                result['pageCount'] = 'Page count not found'
            # check for averageRating
            if 'averageRating' in item['volumeInfo'].keys():
                result['averageRating'] = item['volumeInfo']['averageRating']
            else:
                result['averageRating'] = 'Average rating not found'
            # check for thumbnail
            if 'imageLinks' in item['volumeInfo'].keys():
                result['thumbnail'] = item['volumeInfo']['imageLinks']['thumbnail']
            else:
                result['thumbnail'] = 'Thumbnail not found'
            searchresults.append(result)
        return render_template('searchbooks.html', searchresults=searchresults)
    return render_template('searchbooks.html')


# In[ ]:


@app.route('/searchbooksbytitle', methods=['POST'])
def search_books_by_title():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    # check google for search results
    r = requests.get('https://www.googleapis.com/books/v1/volumes?q=intitle:' + request.form['searchtitle'])
    json = r.json()
    searchresults = []
    for item in json['items']:
        result = {}
        result['title'] = item['volumeInfo']['title']
        # check for authors
        if 'authors' in item['volumeInfo'].keys():
            result['author'] = item['volumeInfo']['authors'][0]
        else:
            result['author'] = 'Author not found'
        # check for pageCount
        if 'pageCount' in item['volumeInfo'].keys():
            result['pageCount'] = item['volumeInfo']['pageCount']
        else:
            result['pageCount'] = 'Page count not found'
        # check for averageRating
        if 'averageRating' in item['volumeInfo'].keys():
            result['averageRating'] = item['volumeInfo']['averageRating']
        else:
            result['averageRating'] = 'Average rating not found'
        # check for thumbnail
        if 'imageLinks' in item['volumeInfo'].keys():
            result['thumbnail'] = item['volumeInfo']['imageLinks']['thumbnail']
        else:
            result['thumbnail'] = 'Thumbnail not found'
        searchresults.append(result)
    return render_template('searchbooks.html', searchresults=searchresults)


# In[ ]:


@app.route('/addbook', methods=['GET'])
def add_book():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    db = get_db()
    cur = db.execute('insert into bookcatalogue (user_id, title, author, page_count, average_rating, thumbnail) values (?, ?, ?, ?, ?, ?)', [session['user_id'], request.args['title'], request.args['author'], request.args['pageCount'], request.args['averageRating'], request.args['thumbnail']])
    db.commit()
    return redirect(url_for('show_books'))


# In[ ]:


@app.route('/deletebook', methods=['GET'])
def delete_book():
    if not session.get('logged_in'):
        redirect(url_for('login'))
    error = None
    db = get_db()
    cur = db.execute('delete from bookcatalogue where user_id=? and title=? and author=? and page_count=? and average_rating=? and thumbnail=?', [session['user_id'], request.args['title'], request.args['author'], request.args['pageCount'], request.args['averageRating'], request.args['thumbnail']])
    db.commit()
    return redirect(url_for('show_books'))


# In[ ]:


if __name__ == '__main__':
    app.run()


# In[ ]:




