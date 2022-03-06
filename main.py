import os
import json
from enum import Enum, auto

from dotenv import load_dotenv
load_dotenv()

from flask import (
    Flask, render_template, request, url_for, flash
)
import requests

app = Flask(__name__)
    
@app.route('/', methods=('GET', 'POST'))
def home():
    page_data = {
        'temperature': None,
        'clothing': None
    }

    if request.method == 'POST':
        zipcode = request.form['zipcode']
        error = None

        valid_zip_input = _validate_zip_code_input(zipcode)

        if not zipcode or not valid_zip_input:
            error = 'Valid 5-digit zip code is required!'
        
        # fetch the weather for zip code
        if error is None:
            weather = _get_weather(zipcode)
            error = weather.get('error', {}).get('message', None)
            
            if error is None:
                page_data['temperature'] = weather.get('current', {}).get('feelslike_f', None)
        
        if page_data['temperature']:
            page_data['clothing'] = _get_clothes(page_data['temperature'])
        
        if error:
            flash(error)

    return render_template('home.html', **page_data)


def _validate_zip_code_input(some_value):
    str_value = str(some_value)
    
    # zip codes have 5 digits
    if len(str_value) != 5:
        return False
    
    # each digit should be an int inbetween 0 and 9 (inclusive)
    for char in str_value:
        try:
            digit = int(char)
            if digit not in range(0, 10):
                return False
        except ValueError:
            return False

    # if the value makes it this far, fairly likely to be a zip
    # the weather API will let us know if this does not correspond to a real location
    return True
    


def _get_weather(zipcode):
    base_url = 'http://api.weatherapi.com/v1'
    current_weather_endpoint = '/current.json'
    params = {
        'key': os.getenv('WEATHER_API_KEY'),
        'q': zipcode
    }
    resp = requests.get(base_url+current_weather_endpoint, params=params)
    return resp.json()


class Category(Enum):
    C1 = range(-100, 37)
    C2 = range(37, 46)
    C3 = range(46, 55)
    C4 = range(55, 66)
    C5 = range(66, 76)
    C6 = range(76, 81)
    C7 = range(81, 180)


def _get_clothes(temperature):
    '''
    ===CLOTHING===
    Headwear: Hat, Beanie
    Tops: Down Jacket, Fleece, tshirt, tank top
    Bottoms: Pants, Shorts, Board Shorts
    Footwear: Heavy socks, light weight socks 

    ===RANGES===
    <36
    Beanie, down jacket, pants, heavy socks

    37-45
    down jacket, pants, heavy socks

    46-54
    fleece, pants, heavy socks

    55-65
    fleece, pants, light socks
    
    66-75
    tshirt, pants, light socks

    76-80
    hat, tshirt, shorts

    >81
    hat, tank top, board shorts
    '''

    # int() will just cut off decimal, call round() first
    input_temp = int(round(float(temperature)))

    # check which range the input temp falls into
    temp_category = None
    for cat in Category:
        if input_temp in cat.value:
            temp_category = cat
            break
    
    if temp_category:
        clothing = _fetch_clothing_options(temp_category)
        return clothing
    
    # return the appropriate clothing
    return None


CLOTHING_DATA = {
    'hat': {
        'img_file': 'hat.jpeg',
        'store_link': 'https://www.patagonia.com/product/baggies-brimmer-hat/33341.html?dwvar_33341_color=TGOR'
    },
    'beanie': {
        'img_file': 'beanie.jpeg',
        'store_link': 'https://www.patagonia.com/product/beanie-hat/28860.html?dwvar_28860_color=BLK'
    },
    'down jacket': {
        'img_file': 'down jacket.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-hi-loft-down-hoody/84902.html?dwvar_84902_color=BARR'
    },
    'fleece': {
        'img_file': 'fleece.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-lightweight-synchilla-snap-t-fleece-pullover/25580.html?dwvar_25580_color=APBL'
    },
    'tshirt': {
        'img_file': 'tshirt.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-fitz-roy-horizons-responsibili-tee/38501.html?dwvar_38501_color=SUMR'
    },
    'tank top': {
        'img_file': 'tank top.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-p-6-label-organic-cotton-tank/38550.html?dwvar_38550_color=FINB'
    },
    'pants': {
        'img_file': 'pants.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-straight-fit-jeans-regular/21625.html?dwvar_21625_color=ORSD'
    },
    'shorts': {
        'img_file': 'shorts.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-all-seasons-hemp-canvas-5-pocket-11-inch-inseam-shorts/57125.html?dwvar_57125_color=FTGN'
    },
    'board shorts': {
        'img_file': 'board shorts.jpeg',
        'store_link': 'https://www.patagonia.com/product/mens-baggies-5-inch-inseam-shorts/57022.html?dwvar_57022_color=FRTL'
    },
    'heavy socks': {
        'img_file': 'heavy socks.jpeg',
        'store_link': 'https://www.patagonia.com/product/heavyweight-merino-performance-knee-length-socks/50115.html?dwvar_50115_color=CFZV'
    },
    'light socks': {
        'img_file': 'light socks.jpeg',
        'store_link': 'https://www.patagonia.com/product/lightweight-merino-performance-knee-socks/50155.html?dwvar_50155_color=BLK'
    },
}


def _fetch_clothing_options(temp_category):
    clothing = {
        Category.C1: [
            CLOTHING_DATA['beanie'],
            CLOTHING_DATA['down jacket'],
            CLOTHING_DATA['pants'],
            CLOTHING_DATA['heavy socks']
        ],
        Category.C2: [
            CLOTHING_DATA['down jacket'],
            CLOTHING_DATA['pants'],
            CLOTHING_DATA['heavy socks']
        ],
        Category.C3: [
            CLOTHING_DATA['fleece'],
            CLOTHING_DATA['pants'],
            CLOTHING_DATA['heavy socks']
        ],
        Category.C4: [
            CLOTHING_DATA['fleece'],
            CLOTHING_DATA['pants'],
            CLOTHING_DATA['light socks']
        ],
        Category.C5: [
            CLOTHING_DATA['tshirt'],
            CLOTHING_DATA['pants'],
            CLOTHING_DATA['light socks']
        ],
        Category.C6: [
            CLOTHING_DATA['hat'],
            CLOTHING_DATA['tshirt'],
            CLOTHING_DATA['shorts']
        ],
        Category.C7: [
            CLOTHING_DATA['hat'],
            CLOTHING_DATA['tank top'],
            CLOTHING_DATA['board shorts']
        ]
    }
    return clothing[temp_category]

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')

if os.getenv('DEV') == 'ON':
    app.run(debug=True)