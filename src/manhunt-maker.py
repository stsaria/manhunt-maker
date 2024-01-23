import subprocess, traceback, requests, datetime, shutil, json, os

url_papermc = "https://api.papermc.io/v2/projects/paper/versions/1.19.4/builds/550/downloads/paper-1.19.4-550.jar"
url_plugins = ["https://github.com/minecraftacted/ManHunt2/releases/download/2.2/manhunt2-2.2.jar"]

def exec_java(dir_name, jar_name, xms : int, xmx : int, java_argument=""):
    try:
        result = subprocess.run(["java", f"-Xmx{str(xmx)}G", f"-Xms{str(xms)}G", "-jar", jar_name]+java_argument.split(" "), cwd=f"{dir_name}/", timeout=3600).returncode
        print(result)
    except subprocess.TimeoutExpired:
        return 0
    except:
        return 1
    return result

def download_file(url : str, save_name : str, user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"):
    try:
        if "http" in url == False:
            url = "http://"+url
        header = {
            'User-Agent': user_agent
        }
        response = requests.get(url, headers=header)
        if not str(response.status_code)[:1] in ["2","3"]:
            return False
        with open(save_name ,mode='wb') as f:
            f.write(response.content)
        return True
    except:
        return False

def make_server(mcid : str):
    global url_papermc
    global url_plugins
    dt_now        = datetime.datetime.now()
    dt_now_utc    = datetime.datetime.now(datetime.timezone.utc)
    try:
        os.makedirs("minecraft/", exist_ok=True)
        os.makedirs("minecraft/plugin", exist_ok=True)
        shutil.copy("config/server.properties.template", f"minecraft/server.properties")
        with open("minecraft/eula.txt", mode='a', encoding='utf-8') as f:
            f.write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n#"+dt_now_utc.strftime('%a')+" "+dt_now_utc.strftime('%b')+" "+dt_now_utc.strftime('%d')+" "+dt_now_utc.strftime('%H:%M:%S')+" "+str(dt_now_utc.tzinfo)+" "+dt_now_utc.strftime('%Y')+"\neula=true")
        if download_file(url_papermc, f"minecraft/server.jar") == False:
            print("Error : Fail download minecraft server")
            return 2
        if download_file(f"https://api.mojang.com/users/profiles/minecraft/{mcid}", f"minecraft/mcid.json") == False:
            print("Error : Fail download mojang api json")
            return 2
        with open(f"minecraft/mcid.json", encoding="utf-8") as f:
            json_dict = json.load(f)
            if not 'id' in json_dict:
                print("Error : Unknow MCID")
                return 3
        with open(f"minecraft/ops.txt", encoding="utf-8", mode="w") as f:
            f.write(f"{mcid}")
        for i in url_plugins:
            if download_file(i, "minecraft/"+i.split("/")[-1]) == False:
                print("Error : Fail download minecraft plugin")
                return 2
        print("Server Make Success.")
        return 0
    except:
        error = traceback.format_exc()
        print(f"Error : Unknow\n\n{error}")
        return 1

def start_server():
    try:
        result = exec_java(f"minecraft/", f"server.jar", 2, 2, java_argument=f"nogui")
        if result != 0:
            print("Error : Error minecraft server")
            return 2
        print("Minecraft server STOP!!")
        return 0
    except:
        error = traceback.format_exc()
        print(f"Error : Unknow\n\n{error}")
        return 1

def main():
    print("Manhunt Maker")
    mcid = input("Please Input Mcid(OP) : ")
    if make_server(mcid) == 0:
        start_server()
    if os.path.isdir("minecraft"): shutil.rmtree("minecraft")

if __name__ == "__main__":
    main()