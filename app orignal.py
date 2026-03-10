import os
import sys
import subprocess


if __name__ == "__main__" and os.environ.get("STREAMLIT_RUN") != "1":
    os.environ["STREAMLIT_RUN"] = "1"
    subprocess.run(["python", "-m", "streamlit", "run", __file__])
    sys.exit()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class RetailPerformanceSystem:

    def __init__(self):
        self.data = None
        self.filtered_data = None
        self.numeric_cols = []

    def setup_page(self):
        st.set_page_config(page_title="Retail Intelligence System", layout="wide")
        st.title("🛒 Retail Sales Intelligence Dashboard")

    def upload_file(self):
        file = st.file_uploader("Upload Retail Sales Dataset", type=["xlsx"])
        if file:
            self.data = pd.read_excel(file)
            return True
        return False

    def preview_data(self):
        st.subheader("📄 Sales Data Overview")
        st.dataframe(self.data, use_container_width=True)
        st.write("Dataset Shape:", self.data.shape)

    def extract_numeric_columns(self):
        self.numeric_cols = self.data.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()

    def apply_filters(self):

        st.sidebar.header("🔎 Sales Filters")
        self.filtered_data = self.data.copy()

        if "Store_Location" in self.data.columns:
            locations = st.sidebar.multiselect(
                "Select Store Location",
                self.data["Store_Location"].unique()
            )

            if locations:
                self.filtered_data = self.filtered_data[
                    self.filtered_data["Store_Location"].isin(locations)
                ]

        if "Product_Category" in self.data.columns:
            categories = st.sidebar.multiselect(
                "Select Product Category",
                self.data["Product_Category"].unique()
            )

            if categories:
                self.filtered_data = self.filtered_data[
                    self.filtered_data["Product_Category"].isin(categories)
                ]

        st.sidebar.write("Filtered Records:", self.filtered_data.shape[0])

    def build_dashboard(self):

        if len(self.numeric_cols) > 0:

            metric = st.selectbox("Select Sales Metric", self.numeric_cols)

            st.markdown("## 📊 Sales Analytics Dashboard")

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            with col1:
                if "Store_Location" in self.filtered_data.columns:
                    st.subheader("Revenue by Location")
                    data = self.filtered_data.groupby("Store_Location")[metric].sum()
                    st.bar_chart(data)

            with col2:
                if "Product_Category" in self.filtered_data.columns:
                    st.subheader("Category Distribution")
                    cat = self.filtered_data["Product_Category"].value_counts()
                    fig, ax = plt.subplots()
                    ax.pie(cat, labels=cat.index, autopct="%1.1f%%")
                    st.pyplot(fig)

            with col3:
                st.subheader("Revenue Distribution")
                fig, ax = plt.subplots()
                sns.histplot(self.filtered_data[metric], bins=20, kde=True, ax=ax)
                st.pyplot(fig)

            with col4:
                if "Payment_Method" in self.filtered_data.columns:
                    st.subheader("Revenue by Payment Method")
                    fig, ax = plt.subplots()
                    sns.boxplot(
                        x="Payment_Method",
                        y=metric,
                        data=self.filtered_data,
                        ax=ax
                    )
                    st.pyplot(fig)

            st.markdown("## 📈 Key Performance Indicators")

            total_revenue = self.filtered_data[metric].sum()
            avg_revenue = self.filtered_data[metric].mean()
            max_sale = self.filtered_data[metric].max()

            if "Units_Sold" in self.filtered_data.columns:
                total_units = self.filtered_data["Units_Sold"].sum()
            else:
                total_units = 0

            k1, k2, k3, k4 = st.columns(4)

            k1.metric("Total Revenue", f"{total_revenue:,.2f}")
            k2.metric("Average Revenue", f"{avg_revenue:,.2f}")
            k3.metric("Highest Sale", f"{max_sale:,.2f}")
            k4.metric("Total Units Sold", total_units)

            if "Date" in self.filtered_data.columns:
                st.markdown("## 📅 Monthly Revenue Trend")

                self.filtered_data["Date"] = pd.to_datetime(
                    self.filtered_data["Date"]
                )

                monthly = self.filtered_data.groupby(
                    self.filtered_data["Date"].dt.to_period("M")
                )[metric].sum()

                monthly.index = monthly.index.astype(str)

                st.line_chart(monthly)


def main():

    app = RetailPerformanceSystem()

    app.setup_page()

    if app.upload_file():
        app.preview_data()
        app.extract_numeric_columns()
        app.apply_filters()
        app.build_dashboard()
    else:
        st.info("Upload Retail Dataset to Begin Analysis.")


if __name__ == "__main__":
    main()

