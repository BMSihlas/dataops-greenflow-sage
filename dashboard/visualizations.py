import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

def plot_bar_chart_column(df, column, title):
    """Generic function to plot a bar chart."""
    st.subheader(title)
    st.bar_chart(df.set_index("company")[column])
    
def plot_bar_chart(data, x, y, ylabel, title=""):
    """Generic function to plot a bar chart using Seaborn and Matplotlib in Streamlit."""
    
    # Create a new figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bar plot
    sns.barplot(data=data, x=x, y=y, hue=x, palette="Blues_r", edgecolor="black", ax=ax, legend=False)

    # Rotate labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

    # Add gridlines
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Add labels on top of bars
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,.0f}', 
                    (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom', fontsize=10, color='black')

    # Set labels and title
    ax.set_xlabel(x.capitalize())  
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=14)

    # Adjust layout
    plt.tight_layout()

    # Use Streamlit to display the figure
    st.pyplot(fig)

def plot_correlation_heatmap(df):
    """Generates a correlation heatmap."""
    st.subheader("📊 Feature Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
