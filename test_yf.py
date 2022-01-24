import datetime
import yfinance 
import streamlit
import pandas
import sys
# -----------------------------------------------------------------------------------------------------------

streamlit.write("""
## Fastest way to a web application: Stock pricing with yfinance and Streamlit 101  
Enter the ticker symbol to generate interesting insights!
""")
tickerSymbol = streamlit.text_input("Ticker", "aapl",max_chars = 6)

#get data on this ticker
tickerData = yfinance.Ticker(tickerSymbol)

try:
# -----------------------------------------------------------------------------------------------------------
# print the details of the asset
# -----------------------------------------------------------------------------------------------------------
    col1, col2 = streamlit.columns(2)
    with col1: 
        streamlit.write("Name: ", tickerData.info["longName"])
        try:
            streamlit.write("Web: ", tickerData.info["website"])
        except:
            streamlit.write("No website found")
    with col2: 
        streamlit.write("Sector: ", tickerData.info["sector"])
        streamlit.write("Industry: ", tickerData.info["industry"])

    streamlit.image(tickerData.info["logo_url"], width=100)

    # print any optional metric
    mydict = tickerData.info
    mykeys = mydict.keys()

    col1, col2 = streamlit.columns(2)
    with col1: 
        physical_form = streamlit.selectbox("Interested in any additional metric? Use the drop down:", options= mykeys)
    with col2: 
        streamlit.write("\n")
        streamlit.write("\n")
        streamlit.write("\n")
        streamlit.write(tickerData.info[physical_form])

    # -----------------------------------------------------------------------------------------------------------
    # Get analyst recommendations
    # -----------------------------------------------------------------------------------------------------------
    # recos = tickerData.recommendations
    recos = pandas.DataFrame(data=tickerData.recommendations)
    recos.reset_index(inplace=True)
    recos = recos.rename(columns = {'index':'Date'})
    recos.columns = ["Date","Firm","Recommendation","From Grade","Action"]
    recos = recos.sort_values(by='Date', ascending=False)
    recos["Date"] = recos["Date"].dt.strftime("%d %b %Y")
    streamlit.write(" #### Analyst recommendations: ",recos[["Date","Firm","Recommendation"]].head(5))

    # -----------------------------------------------------------------------------------------------------------
    # get the historical prices for this ticker
    # -----------------------------------------------------------------------------------------------------------
    tickerDf = tickerData.history(period="max")

    # -----------------------------------------------------------------------------------------------------------
    # plot charts
    # -----------------------------------------------------------------------------------------------------------

    pd_tickerDf = pandas.DataFrame(data=tickerDf)
    pd_tickerDf["intraday"] = 200*abs(pd_tickerDf["High"]-pd_tickerDf["Low"])/(pd_tickerDf["High"] + pd_tickerDf["Low"])

    streamlit.write(""" #### Closing Price (drag the graph for deep-dive)""")
    streamlit.area_chart(tickerDf.Close)

    streamlit.write(""" #### Intraday variation % (drag the graph for deep-dive)""")
    streamlit.line_chart(pd_tickerDf["intraday"])

    streamlit.write(""" #### Volume chart (drag the graph for deep-dive) """)
    streamlit.bar_chart(tickerDf.Volume)

    pd_tickerDf.reset_index(inplace=True)
    pd_tickerDf = pd_tickerDf.rename(columns = {'index':'Date'})
    pd_tickerDf = pd_tickerDf.sort_values(by='Date', ascending=True)

    # -----------------------------------------------------------------------------------------------------------
    # Estimate returns
    # -----------------------------------------------------------------------------------------------------------
    streamlit.write(""" #### Estimate returns""")

    d = streamlit.date_input("Choose a historical date to estimate your returns as of today: ",datetime.date(2019, 7, 6))

    d = pandas.Timestamp(d)
    d_formatted = d.strftime("%d %b %Y")
    pd_tickerDf_afterdate = pd_tickerDf[pd_tickerDf["Date"]>=d]

    close_first = pd_tickerDf_afterdate['Close'].iloc[0]
    close_last = pd_tickerDf_afterdate['Close'].iloc[-1]
    co_name = tickerData.info["longName"]
    if close_first == 0:
        ROI = (close_last-0.01)/0.01
    else:
        ROI = (close_last-close_first)/close_first
    delta_price = close_last - close_first

    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.write("\n") 
        streamlit.write(f"Since {d_formatted} to now, the {co_name} stock has gone up from ${round(close_first,1)} to ${round(close_last,1)}")
    with col2:
        streamlit.metric(label="", value= f"{ROI:.0%}" , delta= round(delta_price,1))


except:
    streamlit.write("No stock with this ticker. Nothing to show.")
