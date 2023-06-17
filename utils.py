import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.colors as mcolors


def get_data(filename):
    water_data = pd.read_table(filename, sep=";", skiprows = [1], 
                           parse_dates={"Datetime" : [0,1]}, decimal = ",",
                           dayfirst=True, encoding='utf-16')
    water_data = water_data.set_index("Datetime")
    return water_data


def get_interesting_intervals(df, columns = ["Flow", "Velocity", "Consumption"]):
    in_use = (
    df[columns]
        .sum(axis=1)
        != 0
    ).astype(int)
    mask = in_use.iloc[1 :] - in_use.iloc[: -1].values
    dt_from = mask[mask == 1].index
    dt_to = mask[mask == -1].index
    interesting_intervals = pd.DataFrame({"From" : dt_from, "To" : dt_to})
    return interesting_intervals


def normalized_df(df):
    normalized=(df-df.min())/(df.max()-df.min())
    return normalized


def plot_interval(df, column, 
                  datefrom, dateto, 
                  ax=None, color=None,
                  background_color="white",
                  n_ticks = 12, figsize=(15,3),
                  datetime_format = '%H:%M',
                  show_legend=False,
                  ylim = None,
                  subtitle = None):
    # prepare new figure if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # prepare data
    interval = df.loc[datefrom:dateto]

    # plot stuff in right color
    if type(color) is list:
        for col, c in zip(column, color):
            ax.plot(interval[col], c=c, label=col)
    else:
        ax.plot(interval[column], c=color)

    # Format x axis
    ax.set_xlim((pd.to_datetime(datefrom), pd.to_datetime(dateto)))
    ax.xaxis.set_major_formatter(md.DateFormatter(datetime_format))
    ax.xaxis.set_major_locator(md.MinuteLocator(byminute = [i*(60//(n_ticks)) for i in range(n_ticks)]))

    # Format y axis
    ax.set_ylim(ylim)

    # Vanity
    ax.set_facecolor(background_color)
    if show_legend:
        ax.legend()
    if subtitle is not None:
        ax.title.set_text(subtitle)

    return ax
    

def plot_by_hour(df, column, datefrom, dateto, time_freq="H", 
                 fig_width = 15, fig_height=2, ylim = None,
                 normalize=False,
                 **kwargs):
    # prepare data
    if normalize: # move to function above
        df = normalized_df(df)

    # prepare additional parameters
    if ylim is None:
        ylim = (df[column].values.min(), df[column].values.max())

    # split into intervals
    date_range = pd.date_range(datefrom, dateto, freq=time_freq)
    n_subplots = len(date_range)-1

    # create plot
    fig, axs = plt.subplots(n_subplots, 1, 
                            figsize=(fig_width, fig_height*n_subplots), 
                            layout="constrained")
    fig.suptitle(f"{column} : {datefrom} - {dateto}")
    
    # plot stuff
    for ax, subdatefrom, subdateto in zip(axs, date_range[:-1], date_range[1:]):
        plot_interval(df, column, subdatefrom, subdateto, 
                      ax = ax, ylim = ylim, 
                      subtitle = f"{subdatefrom} - {subdateto}", **kwargs)

    return fig, axs, date_range


def add_blocks(ax, dates_from, dates_to, colors=None, default_color="xkcd:salmon", colors_table=list(mcolors.TABLEAU_COLORS)):
    if len(dates_from)==0:
        return
    # set color list
    if colors is None:
        colors = [default_color for _ in range(len(dates_from))]
    elif type(colors[0]) is not str:
        colors = [colors_table[color] for color in colors]
    # add blocks
    for datefrom, dateto, color in zip(dates_from, dates_to, colors):
        ax.axvspan(datefrom, dateto, facecolor = color, alpha = 0.5)
    return ax

def add_blocks_to_all(axs, date_range, dates_intervals_df, from_col="From", to_col="To", color_col=None ,**kwargs):
    for ax, date_start, date_stop in zip(axs, date_range[:-1], date_range[1:]):
        filtered_intervals = dates_intervals_df[(dates_intervals_df[from_col]<=date_stop) & (dates_intervals_df[to_col]>=date_start)]
        add_blocks(ax, 
                   filtered_intervals[from_col], 
                   filtered_intervals[to_col], 
                   colors = None if color_col is None else filtered_intervals[color_col].values,
                   **kwargs)