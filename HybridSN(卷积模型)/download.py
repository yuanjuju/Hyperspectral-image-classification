import requests

urls = [
    "http://www.ehu.eus/ccwintco/uploads/6/67/Indian_pines_corrected.mat",
    "http://www.ehu.eus/ccwintco/uploads/c/c4/Indian_pines_gt.mat"
]

save_paths = [
    "D:\python file\classify\classify.venv\data",
    "D:\python file\classify\classify.venv\data"
]

for url, save_path in zip(urls, save_paths):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

print("下载完成！")
