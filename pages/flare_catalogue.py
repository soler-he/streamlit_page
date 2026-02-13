import pooch
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode #, StAggridTheme
from st_aggrid.shared import JsCode
from time import sleep

fname = 'SOLER_Flare_catalogue'  # 'full_catalogue_with_stix_merged_with_cme'

st.title('Flare catalogue')

st.write('This catalogue contains solar flares with a flare class > M5 observed in solar cycle 25, including key characteristics of each flare. The flares in this catalogue were compiled using observation from two spacecraft: the Geostationary Operational Environmental Satellite (GOES) and Solar Orbiter (SolO).')

t_df = pd.read_csv(f'catalogues/{fname}.csv', sep=',')
time_columns = [col for col in t_df.columns if 'Time' in col]



df_flare_org = pd.read_csv(f'catalogues/{fname}.csv', sep=',', parse_dates=time_columns)

def store_value(my_key):
    # Copy the value to the permanent key
    st.session_state[my_key] = st.session_state[f"_{my_key}"]

default_columns = df_flare_org.keys().tolist()
hid_cols = ["Start Time at 1 AU (GOES)", "Start Time at 1 AU (STIX)", "Peak Time at 1 AU (GOES)", "Peak Time at 1 AU (STIX)", "End Time at 1 AU (GOES)", "End Time at 1 AU (STIX)", 
            "Start Time at the Sun (GOES)", "Start Time at the Sun (STIX)", "Peak Time at the Sun (GOES)", "Peak Time at the Sun (STIX)", "End Time at the Sun (GOES)", "End Time at the Sun (STIX)"]
for col in hid_cols:
  default_columns.remove(col)

if 'selected_columns_flare' in st.session_state:
  default_keys = st.session_state.selected_columns_flare
else:
  default_keys = default_columns  # TODO: provides this as an option? show all columns?

st.multiselect("Select columns to display (by default all are active).", options=df_flare_org.keys(), default=default_keys, key='_selected_columns_flare', on_change=store_value, args=["selected_columns_flare"])
# st.multiselect("Select columns to display (by default all are active).", options=df_flare_org.keys(), default=default_keys, key='_selected_columns_flare')
hidden_columns = df_flare_org.keys().tolist()
if 'selected_columns_flare' in st.session_state:
  df_flare = df_flare_org[st.session_state.selected_columns_flare]
  for col in st.session_state.selected_columns_flare:
    hidden_columns.remove(col) 
else:
  df_flare = df_flare_org[default_keys]
  for col in default_keys:
    hidden_columns.remove(col) 
if len(hidden_columns) == 0:
  st.write("All columns are displayed.")
elif len(hidden_columns) > 0:
  with st.expander(f"{len(hidden_columns)} columns hidden (click for details):"):
    st.dataframe(pd.DataFrame(hidden_columns, columns=['Column name']), hide_index=True)
    st.write("To show hidden columns, select them from the multiselect box above.")

gb = GridOptionsBuilder.from_dataframe(df_flare)
# gb.configure_column("# id", header_name='Event ID')
for key in df_flare.keys():
  gb.configure_column(key, tooltipField=str(key), headerTooltip=str(key))
# gb.configure_column("flare_comments", header_name='Flare Comments', tooltipField='flare_comments', headerTooltip='Comments about flares', width=10)

gb.configure_column(
    "IP Radio Bursts",
    headerName="IP Radio Bursts",
    # width=100,
    cellRenderer=JsCode("""
        class UrlCellRenderer {
          init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = params.value;
            this.eGui.setAttribute('href', params.value);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
          }
          getGui() {
            return this.eGui;
          }
        }
    """)
)

# gb.configure_grid_options(onCellDoubleClicked=onCellDoubleClickedHandler)
# gb.configure_grid_options(onCellClicked=onCellDoubleClickedHandler)

# Make NaT values invisible without removing them
cell_stylejscode = JsCode("""
    function(params) {
        console.log(params.value);
        if (params.value === 'NaT') {
            return {
                'color':'rgb(0, 0, 0, 0.0)',
                /// 'backgroundColor':'white'
            }
        }
};
""")
gb.configure_columns(column_names=time_columns, cellStyle = cell_stylejscode)


gridOptions = gb.build() 
gridOptions['rowSelection'] = 'multiple'  # 'multiple'  # 'single'
gridOptions["tooltipShowDelay"] = 500
gridOptions['autoSizeStrategy'] = 'fitCellContents'  # 'fitGridWidth'  # 'fitCellContents'

# Colour rows where STIX start time is NaT
# jscode2 = JsCode("""
# function(params) {
#     if (params.data.event_start_time_stix === 'NaT') {
#         return {
#             'color': 'green',
#             'backgroundColor': 'orange'
#         }
#     }
# };
# """)
# gridOptions['getRowStyle'] = jscode2





# gridOptions["columnDefs"].append(
#     {
#         "field": "clicked",
#         "headerName": "Clicked",
#         "cellRenderer": BtnCellRenderer,
#         "cellRendererParams": {
#             "color": "red",
#             "background_color": "black",
#         },
#     }
# )


grid2 = AgGrid(df_flare, show_toolbar=True, height=500, gridOptions=gridOptions, 
                updateMode=GridUpdateMode.SELECTION_CHANGED,  # GridUpdateMode.VALUE_CHANGED,
                allow_unsafe_jscode=True,
                # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                theme=st.session_state.selected_theme,
                key="table2",
                # update_on = ['selectionChanged'],
                )


# this is a workaround to avoid showing details from previous selection while new selection is being processed until https://github.com/streamlit/streamlit/issues/5044 is resolved.
details_container = st.empty()
details_container.empty()
sleep(0.01)


# try:
#   crocs_link = grid2.data['IP Radio Bursts'][grid2.data.clicked == "clicked"]

#   st.write(crocs_link.values[0])
#   st.write(crocs_link.values[-1])
#   st.image(crocs_link.values[0])
# except AttributeError:
#   pass


with details_container:
    with st.container(border=True):
      if (type(grid2['selected_rows']).__name__ == "NoneType"):
        st.write('Select rows to see details and obtain radio spectrograms!')
      else:
        st.write(grid2['selected_rows'])
        for crocs_link in grid2['selected_rows']['IP Radio Bursts'].values:
          with st.spinner("Downloading figure...", show_time=True):
            fig = pooch.retrieve(url=crocs_link, known_hash=None, progressbar=False)
            st.image(fig)
            # st.image(crocs_link)
        # st.image(grid2['selected_rows']['IP Radio Bursts'].values[0])
        st.write('Plots obtained from https://parker.gsfc.nasa.gov/crocs.html')

st.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">To download a table as csv file, move the mouse over it and click on the <i class="fa-solid fa-download"></i> icon in the top right of the table.', unsafe_allow_html=True)