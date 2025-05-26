#%%
import pandas as pd
import os
from pathlib import Path

DATA_FOLDER = 'data'
URL = "https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx"

def get_data(url):
    df = pd.read_excel(url)

    updated_date = pd.to_datetime(
        df['List of Securities'][0].split(' ')[-1], format='%d/%m/%Y').strftime('%Y-%m-%d')

    df.columns = df.iloc[1]
    df = df.drop([0, 1])
    df['Date'] = updated_date
    # df['Stock Code'] fill leading 0 up to 4 digits
    df['Stock Code'] = df['Stock Code'].astype(int)
    df['Ticker'] = df['Stock Code'].astype(str).apply(lambda x: x.zfill(4)) + '.HK'
    df = df.reset_index(drop=True)
    return df

def get_data_dir(data_folder):
    root_folder = Path(__file__).parent.parent
    data_dir = os.path.join(root_folder, data_folder)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def save_to_csv(df, data_dir, filename='hk_tickers.csv'):
    df.to_csv(os.path.join(data_dir, filename), index=False)

def main():
    df = get_data(URL)
    data_dir = get_data_dir(DATA_FOLDER)
    save_to_csv(df, data_dir)
    return df

def hk_main():
    df = get_data(URL)
    data_dir = get_data_dir(DATA_FOLDER)
    save_to_csv(df, data_dir)
    return df
#%%
if __name__ == '__main__':
    df = main()
    df