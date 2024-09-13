# ExchangeRate
**!IMPORTANT**<p>
There is a basic authorization, so:
<br> login: admin
<br> pass: admin
# Source
The api uses the data from https://bank.gov.ua/NBU_Exchange/exchange_site
<br>
The code then was deployed to pythonanywhere

# Usage and Endpoints
## /exchange_rate {GET}
This will return the currency (<b> by default = $ </b>) exchange rates for a specified period (<b> by default = today </b>)
<br> An example url: <br>
https://frontfliip.pythonanywhere.com/exchange_rate?from=2003-07-23&to=2003-08-23
<br>
The params for period specification are **'to'** and **'from'** 
<br> The result of executing:<br>
![img.png](img.png)
<p>
The format of output is {"date": rate, ...}

## /write_exchange_rate {GET}
This endpoint is used to clear the spreadsheet and write new data to it.<br>
For example for the period from 2015-01-01 to 2022-01-01 the url will look the following way: <br>
https://frontfliip.pythonanywhere.com/write_exchange_rate?from=2015-01-01&to=2022-01-01 <br>
Here is the link to the spreadsheet:<br>
https://docs.google.com/spreadsheets/d/157euJzp2TZ41NsQRkfv-UVDmOsn7XQESBczDx-u03gY/edit?usp=sharing


![img_1.png](img_1.png)
