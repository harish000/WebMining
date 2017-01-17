# Web Mining
A Python application to extract data from the web and run analysis on it.. 
The code snippet allows you to scrape historic stock data from yahoo finance website, preprocess it, store it in MongoDB and run timeseries analysis on it. 
Allows you to visualize the trend of stock returns over a period of one year. 

## Dataset Description
* Date : in days
* Open : price of the stock at the opening of the trading (in US dollars)
* High : highest price of the stock during the trading day (in US dollars)
* Low : lowest price of the stock during the trading day (in US dollars)
* Close : price of the stock at the closing of the trading (in US dollars)
* Volume : amount of stocks traded (in US dollars)
* Adj Close : price of the stock at the closing of the trading adjusted with dividends (in US dollars)

I have used ARIMA Model to project the data over a time period. For more information check out https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average

## Steps to Run
Download the Chrome Web Driver from https://sites.google.com/a/chromium.org/chromedriver/downloads 
Run the program MyScraper.py

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
