from flask import Flask, render_template, request
import pymysql
from cfg import setting_bigdata as setting

hotplace_db = pymysql.connect(
    user=setting.DB_CFG['user'],
    passwd=setting.DB_CFG['passwd'],
    host=setting.DB_CFG['host'],
    db=setting.DB_CFG['db'],
    charset=setting.DB_CFG['charset'])
cur = hotplace_db.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__)
@app.route('/')
def show_main():
    return render_template('show_review_bigdata.html')

@app.route('/review', methods=['POST'])
def show_review():
    _toSearch=""
    _searchCategory="음식점"

    if request.method=='POST':
        _searchCategory = request.form['searchCategory']
        _toSearch = request.form['toSearch']
    
    if(_searchCategory=='음식점'):
        cur.execute("SELECT * FROM HashTag WHERE location LIKE %s LIMIT 200", ('%%%s%%' % _toSearch))
    elif (_searchCategory=='포스트'):
        cur.execute("SELECT * FROM HashTag WHERE post LIKE %s LIMIT 200", ('%%%s%%' % _toSearch))
    elif (_searchCategory=='해시태그'):
        cur.execute("SELECT * FROM HashTag WHERE hashtag LIKE %s LIMIT 200", ('%%%s%%' % _toSearch))
    else:
        cur.execute("SELECT * FROM HashTag WHERE location LIE %s LIMIT 200", ('%%%s%%' % _toSearch))
    _rows = cur.fetchall()

    if _rows:
        return render_template('show_review_bigdata.html', rows=_rows, toSearch=_toSearch, searchCategory=_searchCategory)
    return render_template('show_review_bigdata.html')

@app.route('/new')
def show_new():
    cur.execute("SELECT * FROM HashTag ORDER BY date DESC LIMIT 2000")
    _rows = cur.fetchall()
    if _rows:
            return render_template('show_newsns.html', rows=_rows)
    return render_template('show_newsns.html')

if __name__=='__main__':    
    app.debug=True
    app.run(host='192.168.0.8', port=5000)
