# VWAP Algorithm Project

The objective of this part is to develop a VWAP algorithm sticking close to or even beating the VWAP benchmark.

Assumptions

1) Since there is no average price available for each minute, we will assume the average traded price within each minute as (high + low) / 2.
2) For the analysis, we will only focus on the trading happens in
the regular trading hours (i.e. 9:30am to 4:00pm), including
the open and close auction.
3) Assuming your VWAP algorithm is participating the whole regular trading hours, and trading around 1 million shares per day for analysing your daily trading performance against the VWAP benchmark.
4) If you are not using any data on or after the trading time to make decision, for instance using 9:35am data to make decisions for 9:34am, or using tomorrow’s data to decide the trading behaviour (i.e. using future data to make a decision), it is acceptable.