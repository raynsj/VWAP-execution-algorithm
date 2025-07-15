# Using Temporal Linear Network (TLN) for VWAP execution

## High Level Summary

This report presents a comprehensive implementation and analysis of a Volume Weighted Average Price (VWAP) execution algorithm based on the Temporal Linear Network (TLN) methodology proposed by Remi Genet in their seminal work "Deep Learning for VWAP Execution in Crypto Markets: Beyond the Volume Curve."  Building upon their innovative approach to direct VWAP optimization, I developed an enhanced implementation that incorporates market impact modeling and feature engineering improvements to evaluate real-world trading performance.


The original TLN methodology I used demonstrated promising results in non-market settings, achieving minimal slippage through direct optimization of execution schedules. However, my original implementation reveals significant challenges when realistic market conditions are considered. Initial backtests without market impact model yielded encouraging results with average slippage around 2-3 basis points, consistent with the original paper's findings. However, the incorporation of a square-root market impact model—essential for realistic institutional trading simulation—dramatically altered performance characteristics, resulting in average slippage of ~ 77 basis points. After some extra features being added and fine-tuning, I managed to get the average slippage down to 52.28 basis points with substantial volatility (standard deviation of 58.21 bps).
This dramatic performance degradation highlights a critical limitation in my original TLN framework: the assumption of perfect execution without market impact. While the direct optimization approach represents a significant methodological advancement over traditional two-stage methods, the results demonstrate that real-world implementation requires careful consideration of market microstructure effects that can dominate the optimization benefits.


## VWAP Algorithm Implementation

### Theoretical Foundation

Following the methodology established by the research paper, I implemented a direct optimization approach that bypasses traditional volume curve prediction in favor of end-to-end VWAP minimization. The TLN architecture processes temporal sequences of market data to generate optimal allocation schedules, using a custom loss function that directly minimizes the quadratic difference between model VWAP and benchmark VWAP. This is the core feature of this model.

It lies in the direct optimization paradigm. Rather than following the conventional approach of first predicting volume curves and then deriving execution schedules, the TLN learns to map market conditions directly to optimal trading schedules. This approach theoretically eliminates the compounding errors inherent in two-stage methodologies.
Technical Architecture

My implementation utilizes an enhanced TLN architecture with the following specifications:
* Temporal Window: 120-minute lookback period with 12-minute prediction horizon, optimized from the original paper's recommendations
* Feature Engineering: Expanded from the original 2 features (worked well with no market impact) to 11 comprehensive features including:
* Price and volume data (avg_price, volume)
* Volatility measures (5-minute and 30-minute rolling standard deviation)
* Temporal patterns (hour, minute, day of week)
* Intraday positioning and U-shaped volume pattern weights
* Volume scaling relative to historical averages

**Model Architecture:**
* TLN layer with 3 hidden layers and convolution enabled
* Dropout regularization (0.1) to prevent overfitting
* Batch normalization for training stability
* Softmax activation ensuring valid allocation probabilities


### Loss Function Enhancement

Building upon the original VWAP custom loss function, I implemented an enhanced version incorporating smoothness regularization:

* Loss = α × VWAP_slippage² + β × smoothness_penalty

Where the smoothness penalty discourages erratic allocation changes, promoting more realistic execution patterns. This addition addresses a practical concern not fully explored in the original paper—the tendency for optimization algorithms to generate impractical trading schedules.

### Market Impact Integration

A critical enhancement to the original methodology was the integration of a square-root market impact model:
* Impact = volatility × √(shares_traded / avg_daily_volume)
  
This model, based on established market microstructure research, adjusts execution prices based on trade size and market conditions. The implementation ensures no forward-looking bias by using only historical volatility and volume data available at each decision point.


## In-Depth Performance Analysis and Pain Points

### Performance Metrics and Reality Check

The stark contrast between theoretical and practical performance reveals fundamental limitations in the TLN approach when applied to real trading conditions:

|Metric	|Without| Market |Impact|	With Market Impact|
|Average Slippage	|2-3 bps|	~ 52 bps|
|Standard Deviation	|~13 bps|	~ 58 bps|
|Win Rate|	~62%	|~ 14%|
|Sharpe Ratio	|Positive	|-0.90|


### Critical Pain Points Identified

1.	Market Impact Sensitivity: The most significant finding is the algorithm's extreme sensitivity to market impact. The 2500% increase in average slippage (from ~2 bps to 52 bps) when incorporating realistic market impact suggests that the TLN's optimization may be fundamentally misaligned with market microstructure realities.
2.	High Volatility: The standard deviation of 58.21 bps indicates highly inconsistent performance, with maximum drawdown reaching 182.06 bps. This volatility suggests the algorithm struggles to adapt to varying market conditions.
3.	Poor Risk-Adjusted Returns: The negative Sharpe ratio (-0.90) indicates that the algorithm's returns do not justify the risk taken, making it unsuitable for institutional deployment.
4.	Low Win Rate: Only 14.29% of trading days resulted in negative slippage (outperformance), indicating systematic underperformance relative to the VWAP benchmark.

   
### Theoretical Limitations of the Original TLN Framework

My analysis suggests that the original TLN methodology implicitly assumes frictionless markets—a fundamental assumption that doesn't hold in practice. The paper's focus on direct optimization, while methodologically sound, appears to optimize for an idealized trading environment where:

•	Trades execute at mid-prices without impact
•	Liquidity is infinite
•	Transaction costs are negligible

These assumptions, while necessary for academic research, create a significant gap between theoretical performance and practical applicability.

## Conclusion

This comprehensive implementation and analysis of the TLN methodology for VWAP execution reveals both the promise and limitations of direct optimization approaches. While the paper’s theoretical framework represents a significant advancement in execution algorithm design, my results demonstrate that practical deployment requires careful consideration of market microstructure effects.
The dramatic performance degradation when realistic market impact is considered—from 2-3 bps to over 50 bps average slippage—highlights the critical importance of incorporating market frictions into algorithmic trading research. The original TLN framework, while methodologically innovative, appears optimized for an idealized market environment that diverges significantly from trading reality.
Despite these limitations, the TLN methodology's direct optimization approach remains conceptually valuable. With appropriate modifications to address market impact sensitivity and robustness concerns, this framework could potentially deliver meaningful improvements in institutional execution quality.