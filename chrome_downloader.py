import os
import subprocess
import requests
# from fuzzywuzzy import fuzz
import zipfile
# import sys
import platform


class chrome_webdriver_downloader():

    def get_system_info(self):
        
        self.sys_info ={
        "system": platform.system(),
        "architecture": platform.architecture(),
        # "machine": platform.machine(),
        # "processor": platform.processor(),
        # "platform": platform.platform(),
        # "uname": platform.uname(),
        # "version": platform.version(),
        # "mac_ver": platform.mac_ver(),
        # "linux_distribution": platform.linux_distribution(),
        # "system_alias": platform.system_alias(),
        }



    def get_chrome_version(self,channel='stable'):
        self.get_system_info()

        get_chrome_version_endpoint = ""
        current_chrome_version = ""
        latest_stable_version = ""
        
        if self.sys_info["system"] == "Windows":
            cmd = "reg query \"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon\" /v version"
            chrome_version = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = chrome_version.stdout
            
            current_chrome_version = output.split("    ")[-1].strip()
            get_chrome_version_endpoint = f"https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/{channel}/versions"
            response = requests.get(get_chrome_version_endpoint)
            latest_stable_version = response.json()['versions'][0]['version']

            return {
                "installed_version": current_chrome_version,
                "available_version": latest_stable_version,
                "platform": "win64" if  self.sys_info["architecture"][0] == "64bit" else "win",
                "prefix_version": latest_stable_version.split(".")[0]
            }
        
        elif  self.sys_info["system"] == "Linux":
            cmd = "google-chrome --version"
            chrome_version = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            cmd_out = chrome_version.stdout
            current_chrome_version = cmd_out.split("Google Chrome ")[-1].strip()
            
            get_chrome_version_endpoint = f"https://versionhistory.googleapis.com/v1/chrome/platforms/linux/channels/{channel}/versions"
            response = requests.get(get_chrome_version_endpoint)
            latest_stable_version = response.json()['versions'][0]['version']
            #print(current_chrome_version,latest_stable_version)
            return {
                "installed_version": current_chrome_version,
                "available_version": latest_stable_version,
                "platform": "linux64",
                "prefix_version": latest_stable_version.split(".")[0]
            }

        
        elif  self.sys_info["system"] == "mac_arm64" or  self.sys_info["system"] == "mac":
            get_chrome_version_endpoint = f"https://versionhistory.googleapis.com/v1/chrome/platforms/{ self.sys_info.system}/channels/{channel}/versions"

    
    def file_writer(self,download_link, chrome_details, destination=os.getcwd()):
        try:
            with requests.get(download_link, stream=True) as response:
                response.raise_for_status()  # Raise an HTTPError for bad responses
                with open(f"{destination}/temp.zip", 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive new chunks
                            file.write(chunk)
            
            file_downloaded = True
        
        except requests.exceptions.RequestException as e:
            file_downloaded = False
            print(f"Error downloading file: {e}")

        if file_downloaded == True:
                with zipfile.ZipFile(f"{destination}/temp.zip", 'r') as zip_ref:
                    zip_ref.extractall(destination)
                    print(f"Data has been extracted under this directory: {destination}")
                    return f"{destination}/chromedriver-{chrome_details['platform']}/chromedriver.exe" if "win" in chrome_details['platform'] else f"{destination}/chromedriver-{chrome_details['platform']}//chromedriver"

    def download_chrome_webdriver(self):
        chrome_details = self.get_chrome_version()
        resp = requests.get(f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_details['prefix_version']}")
        download_link = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{resp.text}/{chrome_details['platform']}/chromedriver-{chrome_details['platform']}.zip"
        

        file_path = self.file_writer(download_link,chrome_details)
        print(file_path)

download = chrome_webdriver_downloader()
download.download_chrome_webdriver()