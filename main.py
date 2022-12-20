import streamlit as st
import streamlit.components.v1 as components

import requests
import pandas as pd

from adrubix import RubixHeatmap


def show_code_example():
    st.markdown("Below is the example code from **AdRubix** README for reference.")
    st.code("""
    hm = RubixHeatmap(
        data_path="/home/user/myproject/data/",
        data_file="main_data.csv",
        metadata_rows_file="meta_rows.csv",
        metadata_cols_file="meta_cols.csv",
        plot_save_path="/home/user/myproject/output/plot.html",
        save_png=True,
        scale_along="columns",
        colorbar_title="my colorbar",
        colorbar_location="top",
        show_metadata_rows_labels=True,
        show_rows_legend=False,
        # duplicate_metadata_cols=False,
        colormap_main="fire",
        heatmap_width=1500,
        heatmap_height="proportional",
        data_rows_to_drop=["useless_row_1", "useless_row_2"],
        row_labels_for_highlighting=["row_keyword_A", "row_keyword_B"],
        metadata_col_to_split_rows="Group",
        metadata_row_to_split_cols="Subject",
        nan_color="orange",
        sep_color="green",
        # sep_value="median"
    )
    hm.plot()
    """)


# INTRO
st.set_page_config(layout="wide")
st.markdown("<div id='page_top'></div>", unsafe_allow_html=True)

st.title("AdRubix × Streamlit")
st.subheader("Streamlit GUI for AdRubix")

st.markdown("[AdRubix @ PyPI](https://pypi.org/project/adrubix/)")
with st.expander("PREVIEW ADRUBIX DOCS"):
    resp = requests.get("https://raw.githubusercontent.com/Advestis/adrubix/master/README.md")
    readme_md = resp.text
    st.markdown(readme_md)

st.markdown("1. **Upload your files** in the sidebar")
st.markdown("2. **Set the parameters** in the sidebar (default values are preselected)")
st.markdown("3. Once all the data are uploaded, **visualization** is retriggered by modifying parameter values")
st.markdown("4. You can also **retrigger** it manually by pressing the button  `UPDATE PLOT`")
st.markdown("")

st.sidebar.title("AdRubix parameters")


# DATA INPUT

st.sidebar.markdown("""---""")
st.sidebar.header("Data Files")

data = None
metadata_rows = None
metadata_cols = None

data_file = st.sidebar.file_uploader("Select your MAIN DATA file")
metadata_rows_file = st.sidebar.file_uploader("Select your METADATA for ROWS file")
metadata_cols_file = st.sidebar.file_uploader("Select your METADATA for COLUMNS file")

try:
    data = pd.read_csv(data_file, header=0, index_col=0)
    with st.expander("PREVIEW MAIN DATA"):
        st.dataframe(data, height=600, width=1000)
except ValueError:
    st.warning("Please upload your main data file", icon="⚠️")

try:
    metadata_rows = pd.read_csv(metadata_rows_file, header=0, index_col=0)
    with st.expander("PREVIEW METADATA ROWS"):
        st.dataframe(metadata_rows, height=600)
except ValueError:
    st.warning("Please upload your metadata for rows file", icon="⚠️")

try:
    metadata_cols = pd.read_csv(metadata_cols_file, header=0, index_col=0)
    with st.expander("PREVIEW METADATA COLUMNS"):
        st.dataframe(metadata_cols, height=600)
    st.markdown(f'<p style="text-align:right;"><a href="#plot_top">GO TO PLOT TOP</a></p>', unsafe_allow_html=True)
except ValueError:
    st.warning("Please upload your metadata for columns file", icon="⚠️")

st.markdown("")
save_png = st.sidebar.checkbox("Save plot as PNG image as well")


# DIMENSIONS

st.sidebar.markdown("""---""")
st.sidebar.header("Plot dimensions")
st.sidebar.markdown("For one of the two, you can set `proportional`")

if data is not None:
    hw_default = str(6 * len(data.columns))
    hh_default = str(6 * len(data))
    thresh = 1.2 * float(hh_default)
    hard_thresh = 1000
    hard_thresh_hh = 600
    if float(hh_default) > hard_thresh_hh:
        hh_default = str(round(hard_thresh_hh))
    if float(hw_default) < min(thresh, hard_thresh):
        hw_default = str(round(min(thresh, hard_thresh)))
else:
    hw_default = 1000
    hh_default = 500

heatmap_width = st.sidebar.text_input("Main heatmap width", value=hw_default)
if heatmap_width != "proportional":
    heatmap_width = round(float(heatmap_width))

heatmap_height = st.sidebar.text_input("Main heatmap height", value=hh_default)
if heatmap_height != "proportional":
    heatmap_height = round(float(heatmap_height))

meta_margin = 300
html_width = heatmap_width + meta_margin
html_height = heatmap_height + meta_margin


# DATAPREP

st.sidebar.markdown("""---""")
st.sidebar.header("Dataprep")

scale_along = st.sidebar.selectbox("Scale data along:", ["columns", "rows", "do not scale"], index=0)
if scale_along == "do not scale":
    scale_along = None

normalize_along = st.sidebar.selectbox("Normalize data along:", ["columns", "rows", "do not normalize"], index=2)
if normalize_along == "do not normalize":
    normalize_along = None

color_scaling_quantile = st.sidebar.slider("Color scaling quantile", min_value=80, max_value=100, value=95)

data_rows_to_drop = st.sidebar.text_input("Data rows to drop (Python list syntax)", value="[]")
if data_rows_to_drop == "" or data_rows_to_drop == "[]":
    data_rows_to_drop = None

data_cols_to_drop = st.sidebar.text_input("Data columns to drop (Python list syntax)", value="[]")
if data_cols_to_drop == "" or data_cols_to_drop == "[]":
    data_cols_to_drop = None


# COLORBAR

st.sidebar.markdown("""---""")
st.sidebar.header("Colorbar")

show_colorbar = st.sidebar.checkbox("Show colorbar", value=True)
colorbar_location = st.sidebar.selectbox("Colorbar location", ["top", "center", "bottom"], index=2)
colorbar_title = st.sidebar.text_input("Colorbar title")
colorbar_height = st.sidebar.text_input("Colorbar height (pixels)")
if colorbar_height == "":
    colorbar_height = None
else:
    colorbar_height = round(float(colorbar_height))


# METADATA & LEGENDS

st.sidebar.markdown("""---""")
st.sidebar.header("Metadata")

show_metadata_rows = st.sidebar.checkbox("Show metadata for rows", value=True)
show_metadata_rows_labels = st.sidebar.checkbox("Show labels of the metadata for rows", value=True)
show_metadata_cols = st.sidebar.checkbox("Show metadata for columns", value=True)
duplicate_metadata_cols = st.sidebar.selectbox(
    "Duplicate metadata for columns at the bottom of the heatmap",
    ["no", "yes", "depending on DF size"]
)
if duplicate_metadata_cols == "depending on DF size":
    duplicate_metadata_cols = None
elif duplicate_metadata_cols == "yes":
    duplicate_metadata_cols = True
elif duplicate_metadata_cols == "no":
    duplicate_metadata_cols = False

st.sidebar.markdown("""---""")
st.sidebar.header("Legends")

show_rows_legend = st.sidebar.checkbox("Show the legend for metadata for rows")
show_cols_legend = st.sidebar.checkbox("Show the legend for metadata for columns", value=True)


# COLORMAPS

st.sidebar.markdown("""---""")
st.sidebar.header("Colormaps")

colormap_main = st.sidebar.text_input("Colormap for main data (known by holoviews)", value="coolwarm")
if colormap_main == "":
    colormap_main = None

colormap_metarows = st.sidebar.text_input("Colormap for metadata for rows (known by holoviews)", value="glasbey")
if colormap_metarows == "":
    colormap_metarows = None

colormap_metacols = st.sidebar.text_input("Colormap for metadata for cols (known by holoviews)", value="Category20")
if colormap_metacols == "":
    colormap_metacols = None

nan_color = st.sidebar.color_picker("NaN color", value="#000000")
sep_color = st.sidebar.color_picker("Color of separators", value="#ffffff")

sep_value = st.sidebar.selectbox(
    "Separators behavior",
    ["user-defined color", "min", "median", "adapt"],
)
if sep_value == "user-defined color":
    sep_value = None


# SEPARATORS & HIGHLIGHTING

st.sidebar.markdown("""---""")
st.sidebar.header("Plot enhancement")

metadata_col_to_split_rows = st.sidebar.text_input("Column of metadata for rows to split blocks of data")
if metadata_col_to_split_rows == "":
    metadata_col_to_split_rows = None

metadata_row_to_split_cols = st.sidebar.text_input("Row of metadata for columns to split blocks of data")
if metadata_row_to_split_cols == "":
    metadata_row_to_split_cols = None

row_labels_for_highlighting = st.sidebar.text_input("Row labels for highlighting (Python list syntax)", value="[]")
if row_labels_for_highlighting == "" or row_labels_for_highlighting == "[]":
    row_labels_for_highlighting = None


# PLOT
try:
    hm = RubixHeatmap(
        data=data,
        metadata_rows=metadata_rows,
        metadata_cols=metadata_cols,
        plot_save_path="./tmp.html",
        save_png=save_png,
        scale_along=scale_along,
        normalize_along=normalize_along,
        color_scaling_quantile=color_scaling_quantile,
        data_rows_to_drop=data_rows_to_drop,
        data_cols_to_drop=data_cols_to_drop,
        show_colorbar=show_colorbar,
        colorbar_location=colorbar_location,
        colorbar_title=colorbar_title,
        colorbar_height=colorbar_height,
        show_metadata_rows=show_metadata_rows,
        show_metadata_rows_labels=show_metadata_rows_labels,
        show_metadata_cols=show_metadata_cols,
        duplicate_metadata_cols=duplicate_metadata_cols,
        show_rows_legend=show_rows_legend,
        show_cols_legend=show_cols_legend,
        heatmap_width=heatmap_width,
        heatmap_height=heatmap_height,
        colormap_main=colormap_main,
        colormap_metacols=colormap_metacols,
        colormap_metarows=colormap_metarows,
        nan_color=nan_color,
        sep_color=sep_color,
        sep_value=sep_value,
        metadata_col_to_split_rows=metadata_col_to_split_rows,
        metadata_row_to_split_cols=metadata_row_to_split_cols,
        row_labels_for_highlighting=row_labels_for_highlighting
    )
except FileNotFoundError as e:
    if str(e) == "Data path is not set!":
        pass

st.markdown("<div id='plot_top'></div>", unsafe_allow_html=True)

if data is not None and metadata_rows is not None and metadata_cols is not None:

    st.markdown("""---""")
    st.button("UPDATE PLOT", on_click=hm.plot())

    try:
        html = open("./tmp.html", mode='r', encoding='utf-8')
        source_code = html.read().replace(
            '<body>', '<body style="background-color:white;">'
        )
        components.html(source_code, width=html_width, height=html_height)
        st.markdown(f'<p style="text-align:right;"><a href="#plot_top">BACK TO PLOT TOP</a></p>',
                    unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:right;"><a href="#page_top">BACK TO PAGE TOP</a></p>',
                    unsafe_allow_html=True)

    except FileNotFoundError as e:
        st.error(f"FILE MISSING: {str(e)}", icon="🚨")
