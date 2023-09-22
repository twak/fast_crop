

import pandas as pd


# read in csv file
# for each row
#   for each column
#       if column is a file



if __name__ == "__main__":
    # #read csv
    # df = pd.read_csv(r"~/Downloads/iclr_countr - results_iclr train 1024 test 300.csv")
    df = pd.read_csv(r"~/Downloads/go.csv")
    # # out put as latex table
    #
    styler = df.style
    #
    # styler.format_index(escape="latex")
    #
    # styler.hide(level=0, axis=0)
    #
    # # styler.format_index(escape="latex", axis=1).format_index(escape="latex", axis=0)
    # styler.hide(level=0, axis=0)
    # styler.background_gradient() #cmap='magma', vmin=20, vmax=70)
    # styler.applymap_index(
    #     lambda v: "rotatebox:{90}--rwrap--latex;", level=0, axis=0
    # )
    #
    # print(styler.to_latex(
    #     clines="skip-last;data",
    #     convert_css=True,
    #     position_float="centering",
    #     multicol_align="|c|",
    #     hrules=True))
    # cidx = pd.MultiIndex.from_arrays([
    #     ["Equity", "Equity", "Equity", "Equity",
    #      "Stats", "Stats", "Stats", "Stats", "Rating"],
    #     ["Energy", "Energy", "Consumer", "Consumer", "", "", "", "", ""],
    #     ["BP", "Shell", "H&M", "Unilever",
    #      "Std Dev", "Variance", "52w High", "52w Low", ""]
    # ])
    # iidx = pd.MultiIndex.from_arrays([
    #     ["Equity", "Equity", "Equity", "Equity"],
    #     ["Energy", "Energy", "Consumer", "Consumer"],
    #     ["BP", "Shell", "H&M", "Unilever"]
    # ])
    # styler = pd.DataFrame([
    #     [1, 0.8, 0.66, 0.72, 32.1678, 32.1678 ** 2, 335.12, 240.89, "Buy"],
    #     [0.8, 1.0, 0.69, 0.79, 1.876, 1.876 ** 2, 14.12, 19.78, "Hold"],
    #     [0.66, 0.69, 1.0, 0.86, 7, 7 ** 2, 210.9, 140.6, "Buy"],
    #     [0.72, 0.79, 0.86, 1.0, 213.76, 213.76 ** 2, 2807, 3678, "Sell"],
    # ], columns=cidx, index=iidx).style

    # (styler.format(subset="Equity", precision=2)
    #  .format(subset="Stats", precision=1, thousands=",")
    #  .format(subset="Rating", formatter=str.upper)
    #  .format_index(escape="latex", axis=1)
    #  .format_index(escape="latex", axis=0)
    #  .hide(level=0, axis=0))
    #
    #
    # def rating_color(v):
    #     if v == "Buy":
    #         color = "#33ff85"
    #     elif v == "Sell":
    #         color = "#ff5933"
    #     else:
    #         color = "#ffdd33"
    #     return f"color: {color}; font-weight: bold;"


    # styler.background_gradient(cmap="inferno", subset="columns", vmin=0, vmax=1)
     # .applymap(rating_color, subset="Rating"))

    # styler.applymap_index(
    #     lambda v: "rotatebox:{45}--rwrap--latex;", level=2, axis=1
    # )

    # styler.background_gradient()

    styler.format(precision=2)
    # styler.hide(axis=0)

    print ( styler.to_latex(
        # caption="Selected stock correlation and simple statistics.",
        clines="skip-last;data",
        convert_css=True,
        position_float="centering",
        multicol_align="|c|",
        hrules=True,
    ) )