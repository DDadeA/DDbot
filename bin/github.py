import requests
import os
import shutil

def download_folder_from_github(repo_owner, repo_name, output_folder, folder_path=""):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for item in response.json():
            file_url = item['download_url']
            output_file_path = os.path.join(output_folder, item['path'])

            # Case: Folder
            if (file_url == None):
                if not os.path.exists(output_file_path):
                    os.makedirs(output_file_path)
                download_folder_from_github(repo_owner, repo_name, output_folder, item['path'])
                continue
            
            file_content = requests.get(file_url, headers=headers).content
            with open(output_file_path, 'wb') as output_file:
                output_file.write(file_content)

        print(f"Downloaded successfully to '{output_folder}'.")
    except requests.RequestException as e:
        print("Failed to download the folder:", e)