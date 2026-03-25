import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def visualize_data_matplotlib(csv_path=None):
    if csv_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "sen_results.csv")

    print(f"Reading data from {csv_path}...")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run export_to_csv.py first.")
        return

    df = pd.read_csv(csv_path)

    print("Generating Matplotlib/Seaborn charts...")
    sns.set_theme(style="whitegrid", palette="muted")
    
    # Create a figure with 3 subplots
    fig = plt.figure(figsize=(18, 5))
    
    # 1. Sentiment Distribution (Pie Chart)
    ax1 = plt.subplot(131)
    sentiment_counts = df['sentiment'].value_counts()
    ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
            colors=sns.color_palette("pastel")[0:len(sentiment_counts)], startangle=90)
    ax1.set_title("Sentiment Distribution")

    # 2. Average Score by Tag (Bar Chart)
    ax2 = plt.subplot(132)
    avg_scores = df.groupby('tag')['score'].mean().reset_index().sort_values(by="score", ascending=False)
    sns.barplot(data=avg_scores, x='tag', y='score', ax=ax2, hue='tag', legend=False)
    ax2.set_title("Average Score by Tag")
    ax2.set_xticks(range(len(avg_scores['tag'])))
    ax2.set_xticklabels(avg_scores['tag'], rotation=45, ha='right')

    # 3. Positive vs Negative Word Counts (Scatter Chart)
    ax3 = plt.subplot(133)
    sns.scatterplot(data=df, x='positive_count', y='negative_count', hue='sentiment', 
                    size=df['score'].abs(), sizes=(20, 200), ax=ax3, alpha=0.7)
    ax3.set_title("Positive vs Negative Counts")
    ax3.set_xlabel("Positive Word Count")
    ax3.set_ylabel("Negative Word Count")

    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_png = os.path.join(script_dir, "matplotlib_dashboard.png")
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    
    print(f"Visualization complete! Saved '{output_png}'.")
    plt.show()

if __name__ == "__main__":
    visualize_data_matplotlib()
