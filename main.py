# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask, request, redirect
from datetime import datetime
from flask.helpers import send_from_directory
from google.cloud import datastore
import os, json


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

dataclient = datastore.Client()

@app.route('/favicon.ico')
def favicon_get():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main_page():
    ent = dataclient.key('data', 'posts')
    posts = dataclient.get(key=ent)
    article = ""
    with open('templates/article.html', 'r') as page:
        article = page.read()
    html = ""
    if posts:
        for post in posts['posts']:
            array = json.loads(post)
            raw = article.replace('!content!', array[0])
            raw = raw.replace('!title!', array[1])
            raw = raw.replace('!time!', array[2])
            html += raw
    else:
        html = 'No posts!'
    return applyTemplate('Mitchell\'s MicroBlog', html)

@app.route('/editor')
def edit_page():
    with open('templates/editor.html', 'r') as page:
        editor_html = page.read()
    editor_title = 'Create a Post'
    editor_css = ['https://cdn.jsdelivr.net/npm/sceditor@3/minified/themes/default.min.css']
    return applyTemplate(editor_title, editor_html, editor_css)

@app.route('/submit', methods=['POST'])
def submit_post():
    password = request.form['pass']
    if password == 'securityismypassion':
        content = request.form['content']
        title = request.form['title']
        time = str(datetime.utcnow())
        post = json.dumps([content, title, time])
        ent = dataclient.key('data', 'posts')
        posts = dataclient.get(key=ent)
        if posts:
            posts['posts'] = [post] + posts['posts']
        else:
            posts = datastore.Entity(key=ent)
            posts['posts'] = [post]
        dataclient.put(posts)
    return redirect('/')

@app.route('/instance')
def getid():
    instanceid = os.getenv('GAE_INSTANCE')
    return applyTemplate('Instance ID', str(instanceid))

@app.route('/version-id')
def getversionid():
    versionid = os.getenv('GAE_VERSION')
    return applyTemplate('Version ID', str(versionid))

@app.route('/visitors')
def getVisitors():
    addVisitor()
    ent = dataclient.key('data', 'visitors')
    total = dataclient.get(key=ent)
    result = ''
    if total:
        result = 'Total visitors: ' + str(total['total'])
    else:
        result = 'Total broke!'
    return applyTemplate('Visitors', result)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]

def addVisitor():
    ent = dataclient.key('data', 'visitors')
    total = dataclient.get(key=ent)
    if total:
        total['total'] += 1
        dataclient.put(total)
    else:
        total = datastore.Entity(key=ent)
        total['total'] = 0
        dataclient.put(total)

def applyTemplate(title: str, content: str, css = [], scripts = []):
    with open('templates/template.html', 'r') as template_file:
        template = template_file.read()

    stylesheet_html = ''
    stylesheet_template = '<link rel="stylesheet" href="$url" />'
    for stylesheet in css:
        stylesheet_html += stylesheet_template.replace('$url', stylesheet)
    
    script_html = ''
    script_template = '<script src="$url"></script>'
    for script in scripts:
        script_html += script_template.replace('$url', script)

    template = template.replace('!pageTitle!', title)
    template = template.replace('!stylesheets!', stylesheet_html)
    template = template.replace('!main!', content)
    template = template.replace('!scripts!', script_html)
    return template