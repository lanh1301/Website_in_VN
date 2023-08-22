import numpy as np
import pandas as pd
import requests, langid
from bs4 import BeautifulSoup 
from tqdm import tqdm
import os
import requests


def read_path_file(path_filePath):
    urls    = []
    names   = []
    with open(path_filePath, 'r') as file:
        for line in file:
            if 'crawldiagnostics' not in line :
                break
            
            url = 'https://data.commoncrawl.org/' + line.replace('\n','').replace('crawldiagnostics','warc')
            name = line.replace('\n','').split('/')[-1:][0]
                
            urls.append(url)
            names.append(name)
    return list(zip(names, urls))


def downFile(url_warc, pathSave):
    url = url_warc
    filename = pathSave

    response = requests.get(url, stream=True)

    file_size = int(response.headers.get('Content-Length', 0))

    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)

    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            progress_bar.update(len(chunk))
    progress_bar.close()
    print(f'Dowload file successfully!')
    


def readData(pathData):
    print("Reading Parquet . file...")
    df = pd.read_parquet(path=pathData, engine='fastparquet')
    print("Finished reading the file Parquet!")
    return df


def processing_fileData(data):
    print("Data processing...")
    fetch_status = data.groupby('url_host_private_domain')['fetch_status'].apply(set).reset_index()
    content_languages = data.groupby('url_host_private_domain')['content_languages'].apply(set).reset_index()
    result = data[['url_host_private_domain','fetch_time']].drop_duplicates(subset=['url_host_private_domain'], keep='first')
    result = pd.merge(result, fetch_status, on='url_host_private_domain')
    result = pd.merge(result, content_languages, on='url_host_private_domain')
    result['content_languages'] = content_languages['content_languages'].astype(str).str.slice(1,-1).str.replace("'","").str.replace("None, ","").str.split(',').apply(lambda x: list(set(x)))
    result['fetch_status']  = result['fetch_status'].astype(str).str.slice(1,-1)
    result['content_languages']  = result['content_languages'].astype(str).str.slice(1,-1).str.replace("'","")
    print("Complete data processing!")
    return result


def saveFile(data,file_path):
    file_exists = os.path.isfile(file_path)

    if file_exists:
        data.to_csv(file_path, mode='a', header=False, index=False)
    else:
        data.to_csv(file_path, index=False)

def removeFile(path):
    os.remove(path)
    
    
    
''' 
Phần làm giàu
'''    


'''

'''
def find_url_domain(domain, result):
    url = f"https://{domain}/"
    response = requests.get(url)
    html_content = response.text

    soup_ = BeautifulSoup(html_content, 'html.parser')
    emails = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(soup_))))
    phone_numbers = list(set(re.findall(r'\b\d{10}\b', str(soup_))))
    result['emails']    = emails
    result['phone']     = phone_numbers
    
    for i in soup_.find_all('a'):
        try:
            if 'facebook' in i['href']:
                result['facebook'] = i['href']
            if 'instagram' in i['href']:
                result['instagram'] = i['href']
            if 'youtube' in i['href']:
                result['youtube'] = i['href']
            if 'linkedin' in i['href']:
                result['linkedin'] = i['href']
            if 'twitter' in i['href']:
                result['twitter'] = i['href']
        except:
            i
    return result

def whois(domain):
    url = f"https://www.whois.com/whois/{domain}/"
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    content = soup.find(class_="df-raw")
    return content

from phoneCode import code_phone

def find_country(content,result):
    phone_numbers = re.findall(r"\+\d+\.\d+", content.text)[0]
    Phone_code = phone_numbers.split('.')[0]
    result['phone2'] = phone_numbers
    result['country'] = code_phone[Phone_code]
    return result
