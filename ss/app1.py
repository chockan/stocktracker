from flask import Flask, render_template, request
import requests
import json
import plotly.graph_objs as go

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import requests
import plotly.express as px


def forun():


    app = Flask(__name__)




    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db = SQLAlchemy(app)

    class Stock(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(200), nullable=False)
        price_data = db.Column(db.String(200), nullable=False)
        date_created = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return '<Ticker %r>' % self.id
    with app.app_context():
            # This line will create tables based on the defined models
        db.create_all()
        # index
    @app.route('/add', methods=['POST', 'GET'])
    def add():
        if request.method == 'POST':
            ticker_content = request.form['content']
            price_content = get_stock_price(ticker_content)
            new_ticker = Stock(content=ticker_content, price_data=price_content)

            try:
                db.session.add(new_ticker)
                db.session.commit()
                return redirect('/add')
            except:
                return 'There was an issue adding your ticker'

        else:
            tickers = Stock.query.order_by(Stock.date_created).all()
            return render_template('table.html', tickers=tickers)
        # Update
        
        
    @app.route('/table')
    def table():
        return render_template('table.html')

    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    def update(id):
        ticker = Stock.query.get_or_404(id)

        if request.method == 'POST':
            new_ticker_content = request.form['content']
            new_price_data = get_stock_price(new_ticker_content)

            if new_price_data != 'Not Available':
                ticker.content = new_ticker_content
                ticker.price_data = new_price_data

                try:
                    db.session.commit()
                    return redirect('/add')
                except:
                    return 'There was an issue updating your task'
            else:
                return 'Unable to fetch price data for the updated ticker'
        else:
            return render_template('update.html', ticker=ticker)


        # Delete
    @app.route('/delete/<int:id>')
    def delete(id):
        ticker_to_delete = Stock.query.get_or_404(id)

        try:
            db.session.delete(ticker_to_delete)
            db.session.commit()
            return redirect('/add')
        except:
            return 'There was a problem deleting that task'

        # Function to get stock price using IEX Cloud API
    def get_stock_price(ticker):
        try:
            api_key = 'pk_926bc85cf8044080acbb9bec704a2749'
            url = f'https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={api_key}'
            response = requests.get(url)
                
            if response.status_code == 200:
                data = response.json()
                return data.get('latestPrice', 'Not Available please give valid stock price tricker symbol')
            else:
                return 'Not Available please give valid stock price tricker symbol'
        except requests.RequestException:
            return 'Not Available please give valid stock price tricker symbol'









    def fetch_stock_data(ticker):
        try:
            api_key = 'pk_926bc85cf8044080acbb9bec704a2749'  # Replace with your IEX Cloud API key
            price_url = f'https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={api_key}'
            price_response = requests.get(price_url)
            
            if price_response.status_code == 200:
                price_data = price_response.json()
                current_price = price_data.get('latestPrice', 'Not Available')
            else:
                current_price = 'Not Available'

            chart_url = f'https://cloud.iexapis.com/stable/stock/{ticker}/chart/1y?token={api_key}'
            chart_response = requests.get(chart_url)
            
            if chart_response.status_code == 200:
                chart_data = chart_response.json()
                chart_info = [{
                    'Date': entry['date'],
                    'Low': entry['low'],
                    'High': entry['high'],
                    'Open': entry['open'],
                    'Close': entry['close']
                } for entry in chart_data]
                
                return current_price, chart_info
            else:
                return 'Not Available please give valid stock price tricker symbol', []
        except requests.RequestException:
            return 'Not Available please give valid stock price tricker symbol', []

    @app.route('/')
    def front():
        return render_template('home.html')
    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/index', methods=['GET', 'POST'])
    def index():
        current_price = None
        stock_name = None
        candlestick_chart = None

        if request.method == 'POST':
            ticker_content = request.form['content']
            current_price, chart_info = fetch_stock_data(ticker_content)
            
            
            if chart_info:
                try:
                    stock_name = ticker_content
                    fig = go.Figure(data=[go.Candlestick(x=[entry['Date'] for entry in chart_info],
                                                        open=[entry['Open'] for entry in chart_info],
                                                        high=[entry['High'] for entry in chart_info],
                                                        low=[entry['Low'] for entry in chart_info],
                                                        close=[entry['Close'] for entry in chart_info])])
                    
                    fig.update_layout(title=f'Candlestick Chart for {ticker_content}',
                                    plot_bgcolor='black',  # Set background color to black
                                    paper_bgcolor='black',  # Set paper color to black
                                    font=dict(color='brown'),  # Set font color to white
                                    xaxis=dict(linecolor='white'),  # Set x-axis line color to white
                                    yaxis=dict(linecolor='white'))  # Set y-axis line color to white
                    candlestick_chart = fig.to_html(full_html=False, default_height=670)
                except Exception as e:
                    print(f"Error creating candlestick chart: {e}")
                    # Set candlestick_chart to None or an error message HTML string
                    candlestick_chart = "<p>Error generating chart please give valid stock price tricker symbol</p>"
            else:
                # Set candlestick_chart to None or an error message HTML string
                candlestick_chart = "<p>No chart data available please give valid stock price tricker symbol</p>"


            

        return render_template('index.html',current_price=current_price, stock_name=stock_name, candlestick_chart=candlestick_chart)
    
    return app


    # Your Stock model and fetch_stock_data function here





if __name__ == '__main__':
    app=forun()
    app.run(debug=True)


