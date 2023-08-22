from setting import PATH_FILE_INDEX, PATH_SAVE
from Utils import read_path_file, readData, downFile, processing_fileData, saveFile, removeFile


file = read_path_file(PATH_FILE_INDEX)
for name, url in file[:2]:
    PATH_FILE_PARQUET   = PATH_SAVE + name
    PATH_FILE_CSV       = PATH_SAVE + '\data.csv'
    
    downFile(url,PATH_FILE_PARQUET)
    df = readData(PATH_FILE_PARQUET)
    data = processing_fileData(df)
    print(data.head())
    saveFile(data, PATH_FILE_CSV)
    removeFile(PATH_FILE_PARQUET)
    del df, data
print('The execution is complete!') 
    