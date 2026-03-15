#!/usr/bin/env python3
"""
AION Market Sentiment - Example Output Generator

Generates sample output for documentation purposes.
NO database connections - uses hardcoded sample data.
"""

def main():
    print("=" * 70)
    print("AION Market Sentiment - Example Output")
    print("=" * 70)
    
    # Sample output (hardcoded for documentation)
    print("\n### Sentiment Analysis Output\n")
    print("Headline                              | Sentiment | Confidence | VIX-Adjusted (LOW) | VIX-Adjusted (PANIC)")
    print("-" * 70)
    
    examples = [
        ("Reliance reports record profits", "positive", 93.8),
        ("Market crashes on recession fears", "negative", 90.5),
        ("TCS wins major digital deal", "positive", 88.8),
        ("HDFC Bank expands rural presence", "positive", 85.2),
        ("Trading volume remains average", "neutral", 94.5),
    ]
    
    for headline, sentiment, conf in examples:
        conf_low = conf  # LOW VIX = no adjustment
        conf_high = conf * 0.5  # PANIC VIX = 50% discount
        
        print(f"{headline:35} | {sentiment:9} | {conf:6.1f}%    | {conf_low:6.1f}%             | {conf_high:6.1f}%")
    
    print("\n### Sector Sentiment Heatmap\n")
    print("Sector              | Bullish | Neutral | Bearish | Net Sentiment")
    print("-" * 70)
    
    sectors = [
        ("Banking", 65, 25, 10),
        ("IT", 72, 20, 8),
        ("Auto", 45, 35, 20),
        ("FMCG", 58, 30, 12),
        ("Metal", 30, 40, 30),
    ]
    
    for sector, bullish, neutral, bearish in sectors:
        net = bullish - bearish
        print(f"{sector:17} |   {bullish:5.1f}%   |   {neutral:5.1f}%   |   {bearish:5.1f}%   |     {net:+5.1f}%")
    
    print("\n### Historical Impact Analysis\n")
    print('Query: "Market crashes on recession fears"\n')
    print("Similar Historical News (last 30 days):")
    
    historical_examples = [
        ("Stock market tumbles on recession fears", -2.5),
        ("Investors panic as banks collapse", -3.8),
        ("Banking crisis spreads across Europe", -2.9),
    ]
    
    for headline, impact in historical_examples:
        print(f"  {headline:45} → {impact:+.1f}% (next day)")
    
    avg_impact = sum([x[1] for x in historical_examples]) / len(historical_examples)
    print(f"\nAverage 1-day Impact: {avg_impact:.2f}%")
    
    print("\n### VIX Regime Reference\n")
    print("VIX Level | Regime  | Confidence Multiplier | Position Sizing")
    print("-" * 70)
    print("  <12     | LOW     | 1.0x (100%)           | Full size")
    print("  12-15   | NORMAL  | 1.0x (100%)           | Full size")
    print("  15-25   | HIGH    | 0.8x (80%)            | Reduce 20%")
    print("  ≥25     | PANIC   | 0.5x (50%)            | Reduce 50%")
    
    print("\n" + "=" * 70)
    print("\n✅ All examples use hardcoded sample data - NO database required!")
    print("   Real usage: Connect to your data sources as needed.")

if __name__ == "__main__":
    main()
