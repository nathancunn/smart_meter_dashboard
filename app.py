
import pandas as pd
import streamlit as st

from itertools import product
from plotnine import *


tariff = pd.DataFrame(
    product(range(7), range(24)),
    columns = ["wday", "hour"]
)
tariff["cost"] = 0.2891
tariff.loc[(tariff.hour >= 8) & (tariff.hour < 23), "cost"] = 0.3916
tariff.loc[(tariff.hour >= 17) & (tariff.hour <= 19), "cost"] = 0.4768
tariff["wday"] = tariff.wday.map({
    0:"Mon",
    1:"Tue",
    2:"Wed",
    3:"Thu",
    4:"Fri",
    5:"Sat",
    6:"Sun"
})
st.write(tariff)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)
    dataframe["date"] = pd.to_datetime(dataframe["Read Date and End Time"], dayfirst = True)

    dataframe["wday"] =  dataframe.date.dt.day_name().apply(lambda x: x[:3])
    dataframe["hour"] =  dataframe.date.dt.hour
    agg_df = dataframe.groupby(["wday", "hour"])[["Read Value"]].mean().reset_index()
    agg_df = agg_df.merge(tariff)
    st.write(agg_df)
    fig = (
        ggplot(
            agg_df, 
            aes(
                x = "hour", 
                y = "wday", 
                fill = "Read Value",
                )) + 
                geom_tile(colour = "#FFFFFF") + 
                coord_fixed(ratio = 1, expand = False) +
                scale_fill_continuous(cmap_name="plasma") + 
                scale_y_discrete(limits = [
                    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
                ][::-1]) + 
                theme(axis_title = element_blank())

        )
    st.pyplot(ggplot.draw(fig))
    st.metric("Avg. cost per week", (agg_df.cost * agg_df["Read Value"]).sum())
    cost_df = agg_df.groupby("cost")[["Read Value"]].sum().reset_index()
    cost_df = cost_df.sort_values("cost", ascending = False)
    cost_df["total_cost"] = cost_df.cost * cost_df["Read Value"]
    cost_df["cost_cumsum"] = cost_df.total_cost.cumsum()
    cost_df["cost_start"] = cost_df.cost_cumsum.shift(1).fillna(0)

    cost_df["kwh_cumsum"] = cost_df["Read Value"].cumsum()
    cost_df["kwh_start"] = cost_df.kwh_cumsum.shift(1).fillna(0)
    cost_df["cost"] = pd.Categorical(cost_df.cost, cost_df.cost)
    p = (ggplot(
        cost_df,
        aes(
            xmin = "kwh_start", 
            xmax = "kwh_cumsum", 
            ymin = 0,
            ymax = "total_cost",
            fill = "cost")
    ) + geom_rect()
    + scale_fill_discrete(cmap_name = "plasma")
    + labs(
        x = "Weekly consumption",
        y = "Contribution to weekly bill",
        fill = "Tariff"
        )
    )
    st.pyplot(ggplot.draw(p))

    st.write(cost_df)

