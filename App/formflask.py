# import urllib, requests, socket, urllib3, re, lxml, io, bs4, scrapy, sqlite3, pandas, os
import urllib.request
from bs4 import BeautifulSoup
import sqlite3

from flask import Flask, request, render_template,jsonify
app = Flask(__name__, template_folder='templates')






@app.route('/')
def home():
    return render_template('flaskApp.html')

if __name__ == '__main__':
    app.run(debug=True)