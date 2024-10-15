# Backtests

Project was to test a backtesting library/tool 

Makes api calls out to polygon.io for stock data, then runs some algorithms and code to generate a backtest of a trading strategy based on Expoential moving average time series trend lines. Kinda okay likely not realistic but interesting.

Trading strategy is to trade in tiny frations and only buy and almost never sell. Presumption is SPY always goes up due to current financial system, crashes happen but stonks always goes up. Inflation, pension funds etc. over a long period of time there is a lot of driving force to lift the market index. 

We can see the tests show this automatic trading strategy, which is a simple rule based around exponential moving average executes buy trades during dips and sells near peaks, despite not being told to as it executes it just guesses when to buy and sell. The arrows showing buy and sell points nicely aggregate around peaks and troughs due to this rule tho.

There is also a rule that if a certain position makes more than a specific percentage gain e.g. 1-2% the then we are to sell the position.

Only major drawdown in portfolio is during a crash-like scenario as the buy and selling algorithm in place is to buy in tiny fractions into dips as the market declines. Once a certain max percentage of the portfolio is used up in buying stock then it stops purchases. 

The benefit in my eyes to this approach is typically having an algorithm buying into "troughs" and not "peaks", overal portfolio allocation is a lot lower on average during normal market conditions so risk overall is lower but the overal gains made is lower than the market average. 

This test would be good to test in more choppy and bad market conditions/data. The blue line at the top denotes overall portfolio value whcih never truly declines all that much however cash on hand in the account is heavily used up during crashes. It would be a good idea to reduce the overal maximum portfolio allocation to help reduce this loss in portfolio purchasing power.

Max draw down of cash on hand is around 80% of portfolio value but typical cash drawdowns is a lot lower than that. portfolio value steadily climbs however.

Only goes back 2-3 years of data which is nothing. Only noticeable drop was around COVID 2020-ish about 30-40% drop in market but then money printer. Also since market history shows unprecedencted climbs/recovery in this period the account comes out on top after the 2 year period. Again to stress and re-iterate would be very interesting to see this tested on data with not so optimal conditions.

As a comparison if we we're to all in and buy during the covid peak at aroud $460 and crashed, then held the position. The portfolio would of gained more than 20% since that peak. The issues is however we can never predict the future. Thus having smaller trades and using less portfolio purchasing power lets us dollar cost average and slowly hold out against bad economic conditions/stagnating periods. I feel the trade of in gains is made up by the sustainability aspect of this more conservative approach.


![Alt text](./images/example_1.png)
