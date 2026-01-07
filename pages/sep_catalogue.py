import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode #, StAggridTheme
from st_aggrid.shared import JsCode
from time import sleep

fname = 'SOLER_SEP_catalogue'  # 'full_catalogue_with_stix_merged_with_cme'

st.title('SEP catalogue')

st.write('This catalogue contains multi-spacecraft solar energetic particle (SEP) events, which were observed with the new spacecraft fleet in solar cycle 25. The catalogue comprises key SEP characteristics observed by five different observer locations as provided by Solar Orbiter, Parker Solar Probe, STEREO A, Wind and SOHO (at the Lagrangian point 1), and BepiColombo. The catalogue focuses on large events, which show energetic proton increases above 25 MeV. The catalogue provides not only key parameters of the proton event but also the same parameters for 1 MeV and 100 keV electrons, respectively.')

t_df = pd.read_csv(f'catalogues/{fname}.csv', sep=',')
datetime_columns = [col for col in t_df.columns if 'yyyy-mm-dd' in col]
date_columns = [col for col in t_df.columns if 'yyyy-mm-dd' in col]
time_columns = [col for col in t_df.columns if 'HH:MM:SS' in col]
intensity_columns = ['p25MeV peak flux', 'e1MeV peak flux', 'e100keV peak flux', 'e1MeV peak flux proxy', 'e100keV peak flux proxy']

df_sep_org = pd.read_csv(f'catalogues/{fname}.csv', sep=',')  # , parse_dates=datetime_columns)

# Convert floats to strings formatted in scientific notation
for key in intensity_columns:
  df_sep_org[key] = df_sep_org[key].apply(lambda x: f"{x:.2e}")

def store_value(my_key):
    # Copy the value to the permanent key
    st.session_state[my_key] = st.session_state[f"_{my_key}"]


st.write("Select spacecraft to include data from:")
with st.container(horizontal=True):
  spacecraft = {}
  spacecraft['bepi'] = 'BepiColombo'
  spacecraft['l1'] = 'L1 (SOHO/Wind)'
  spacecraft['psp'] = 'PSP'
  spacecraft['solo'] = 'SOLO'
  spacecraft['sta'] = 'STEREO-A'

  default_sc = {}
  for sc in spacecraft.keys():
    if f'sc_{sc}' in st.session_state:
      default_sc[sc] = st.session_state[f'sc_{sc}']
    else:
      default_sc[sc] = True

  st.checkbox("BepiColombo", value=default_sc['bepi'], key='_sc_bepi', on_change=store_value, args=["sc_bepi"])
  st.checkbox("L1 (SOHO/Wind)", value=default_sc['l1'], key='_sc_l1', on_change=store_value, args=["sc_l1"])
  st.checkbox("Parker Solar Probe", value=default_sc['psp'], key='_sc_psp', on_change=store_value, args=["sc_psp"])
  st.checkbox("Solar Orbiter", value=default_sc['solo'], key='_sc_solo', on_change=store_value, args=["sc_solo"])
  st.checkbox("STEREO-A", value=default_sc['sta'], key='_sc_sta', on_change=store_value, args=["sc_sta"])

sc_list = []
for sc in spacecraft.keys():
  if default_sc[sc]:
    sc_list.append(spacecraft[sc])

if 'Observer' in df_sep_org.columns:
  df_sep_org = df_sep_org.loc[df_sep_org['Observer'].isin(sc_list)]



default_columns = pd.read_csv('catalogues/SOLER_SEP_catalogue_columns.csv', header=None).values.flatten().tolist()

# df = df[['Column1', 'Column2', 'Column3']]

# select columns to display
if 'selected_columns_sep' in st.session_state:
  default_keys = st.session_state.selected_columns_sep
else:
  default_keys = default_columns  # TODO: provides this as an option? show all columns?

st.multiselect("Select columns to display (by default only a selection is active; click below to add hidden columns).", options=df_sep_org.keys(), default=default_keys, key='_selected_columns_sep', on_change=store_value, args=["selected_columns_sep"])
hidden_columns = df_sep_org.keys().tolist()
if 'selected_columns_sep' in st.session_state:
  df_sep = df_sep_org[st.session_state.selected_columns_sep]
  for col in st.session_state.selected_columns_sep:
    hidden_columns.remove(col) 
else:
  df_sep = df_sep_org[default_keys]
  for col in default_keys:
    hidden_columns.remove(col) 
if len(hidden_columns) == 0:
  st.write("All columns are displayed.")
elif len(hidden_columns) > 0:
  with st.expander(f"{len(hidden_columns)} columns hidden (click for details):"):
    st.dataframe(pd.DataFrame(hidden_columns, columns=['Column name']), hide_index=True)
    st.write("To show hidden columns, select them from the multiselect box above.")


gb = GridOptionsBuilder.from_dataframe(df_sep)
for key in df_sep.keys():
  gb.configure_column(key, tooltipField=str(key), headerTooltip=str(key))
# gb.configure_column("flare_comments", header_name='Flare Comments', tooltipField='flare_comments', headerTooltip='Comments about flares', width=10)

# Make nan values invisible without removing them
cell_style_nan = JsCode("""
    function(params) {
        console.log(params.value);
        if (params.value === 'nan') {
            return {
                'color':'rgb(0, 0, 0, 0.0)',
                /// 'backgroundColor':'white'
            }
        }
};
""")
gb.configure_columns(column_names=intensity_columns, cellStyle=cell_style_nan)

# Make NaT values invisible without removing them
cell_style_NaT = JsCode("""
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
# gb.configure_columns(column_names=date_columns, cellDataType='date', type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='yyyy-MM-dd', cellStyle=cell_style_NaT)
gb.configure_columns(column_names=date_columns, type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='yyyy-MM-dd', cellStyle=cell_style_NaT)

for key in ["SEP_IDX", "FLARE_IDX", "CME_IDX", "Event No", "event number"]:
  if key in df_sep.columns:
    gb.configure_column(key, spanRows='true')

gridOptions = gb.build() 
gridOptions['rowSelection'] = 'single'  # 'multiple'  # 'single'
gridOptions["tooltipShowDelay"] = 500
gridOptions['autoSizeStrategy'] = 'fitCellContents'  # 'fitGridWidth'  # 'fitCellContents'
gridOptions['enableCellSpan'] = 'true'
gridOptions['suppressColumnVirtualisation'] = True



grid3 = AgGrid(df_sep, show_toolbar=True, height=500, gridOptions=gridOptions, 
                updateMode=GridUpdateMode.SELECTION_CHANGED,  # GridUpdateMode.VALUE_CHANGED,
                allow_unsafe_jscode=True,
                # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                theme=st.session_state.selected_theme,
                key="table3",
                # update_on = ['selectionChanged'],
                )


# this is a workaround to avoid showing details from previous selection while new selection is being processed until https://github.com/streamlit/streamlit/issues/5044 is resolved.
details_container = st.empty()
details_container.empty()
sleep(0.01)


if (type(grid3['selected_rows']).__name__ == "NoneType"):
  st.write('Select rows to see details!')
else:
  st.write(grid3['selected_rows'])