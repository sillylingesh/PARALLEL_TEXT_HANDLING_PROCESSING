import pandas as pd
import os
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Scatter, Page
from pyecharts.globals import ThemeType

def visualize_data(csv_path=None):
    if csv_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "sen_results.csv")

    print(f"Reading data from {csv_path}...")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run export_to_csv.py first.")
        return

    df = pd.read_csv(csv_path)

    print("Generating charts...")

    # 1. Sentiment Distribution (Pie Chart)
    sentiment_counts = df['sentiment'].value_counts()
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.WONDERLAND))
        .add(
            "",
            [list(z) for z in zip(sentiment_counts.index.tolist(), sentiment_counts.values.tolist())],
            radius=["40%", "70%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Sentiment Distribution"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
    )

    # 2. Average Score by Tag (Bar Chart)
    avg_scores = df.groupby('tag')['score'].mean().reset_index()
    # Sort for better visualization
    avg_scores = avg_scores.sort_values(by="score", ascending=False)
    
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
        .add_xaxis(avg_scores['tag'].tolist())
        .add_yaxis("Average Score", avg_scores['score'].round(2).tolist(), color="#5470c6")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Average Score by Tag"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
            yaxis_opts=opts.AxisOpts(name="Score"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True, position="top"),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="Overall Average")]
            ),
        )
    )

    # 3. Positive vs Negative Word Counts (Scatter Chart)
    # We use size to represent the absolute score magnitude
    sizes = df['score'].abs() * 5 + 5 # Scale for visibility
    
    scatter = (
        Scatter(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add_xaxis(df['positive_count'].tolist())
        .add_yaxis(
            "Sentences",
            df['negative_count'].tolist(),
            symbol_size=20, # Using fixed size if dynamic size is complex across themes
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Positive vs Negative Counts"),
            xaxis_opts=opts.AxisOpts(
                type_="value", splitline_opts=opts.SplitLineOpts(is_show=True),
                name="Positive Word Count"
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value", splitline_opts=opts.SplitLineOpts(is_show=True),
                name="Negative Word Count"
            ),
            visualmap_opts=opts.VisualMapOpts(
                type_="color", 
                max_=df['score'].max(), min_=df['score'].min(),
                dimension=2 # Try to map score to color if possible, though Scatter complex
            )
        )
    )

    # Layout using Page (combining charts into one HTML)
    page = Page(layout=Page.SimplePageLayout)
    page.add(pie, bar, scatter)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_html = os.path.join(script_dir, "dashboard.html")
    page.render(output_html)
    print(f"Visualization complete! Open '{output_html}' in your browser.")


if __name__ == "__main__":
    visualize_data()
