import os
import subprocess
import argparse

def git_configure():
    try:
        subprocess.run(["git", "config", "user.name"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "config", "--global", "user.name", "vnotvirus"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "itsv@rill.cuy"], check=True)

def list_apps():
    result = subprocess.run(["heroku", "apps"], capture_output=True, text=True)
    apps = [line.split()[0] for line in result.stdout.splitlines() if line and not line.startswith("=")]
    print("Daftar aplikasi Heroku:")
    for idx, app in enumerate(apps, start=1):
        print(f"{idx}. {app}")
    return apps

def choose_app(apps):
    try:
        choice = int(input("Pilih nomor aplikasi: "))
        if 1 <= choice <= len(apps):
            return apps[choice - 1]
        else:
            print("Nomor aplikasi tidak valid.")
            return None
    except ValueError:
        print("Input tidak valid.")
        return None

def delete_app_by_name():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        subprocess.run(["heroku", "apps:destroy", "--app", nameapp, "--confirm", nameapp])
        print(f"Aplikasi {nameapp} telah dihapus.")

def delete_all_apps():
    apps = list_apps()
    for app in apps:
        subprocess.run(["heroku", "apps:destroy", "--app", app, "--confirm", app])
        print(f"Aplikasi {app} telah dihapus.")

def check_dynos():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        subprocess.run(["heroku", "ps", "--app", nameapp])

def restart_dynos():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        subprocess.run(["heroku", "ps:restart", "--app", nameapp])
        print(f"Dynos pada aplikasi {nameapp} telah di-restart.")

def restart_all_dynos():
    apps = list_apps()
    for app in apps:
        subprocess.run(["heroku", "ps:restart", "--app", app])
        print(f"Dynos pada aplikasi {app} telah di-restart.")

def change_dyno_type():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        dyno_type = input("Masukkan tipe dyno (eco/basic): ").strip().lower()
        if dyno_type == 'eco':
            type_code = 'eco'
        elif dyno_type == 'basic':
            type_code = 'standard-1x'
        else:
            print("Tipe dyno tidak valid.")
            return

        subprocess.run(["heroku", "ps:type", type_code, "--app", nameapp])
        print(f"Tipe dyno pada aplikasi {nameapp} telah diubah menjadi {dyno_type}.")

def change_all_dyno_types():
    dyno_type = input("Masukkan tipe dyno (eco/basic): ").strip().lower()
    if dyno_type == 'eco':
        type_code = 'eco'
    elif dyno_type == 'basic':
        type_code = 'standard-1x'
    else:
        print("Tipe dyno tidak valid.")
        return

    apps = list_apps()
    for app in apps:
        subprocess.run(["heroku", "ps:type", type_code, "--app", app])
        print(f"Tipe dyno pada aplikasi {app} telah diubah menjadi {dyno_type}.")

def view_logs():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        subprocess.run(["heroku", "logs", "--tail", "--app", nameapp])

def deploy_app():
    nameapp = input("NAMA APP?: ") + "-app"
    git_configure()
    os.system("rm -rf .git")
    subprocess.run(["heroku", "create", nameapp])
    os.system("git init")
    subprocess.run(["heroku", "git:remote", "-a", nameapp])
    
    print("Deploy ke apa:")
    print("1. Node.js")
    print("2. PHP")
    choice = input("Masukkan pilihan Anda (default 1): ") or '1'

    buildpack = "heroku/nodejs" if choice == '1' else "heroku/php"

    subprocess.run(["heroku", "buildpacks:set", buildpack, "--app", nameapp])

    with open(".gitignore", "w") as f:
        if choice == '2':
            f.write("vendor/\n.env")
        else:
            f.write("node_modules/")
    
    os.system("git add .")
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    subprocess.run(["git", "push", "heroku", "master"])
    print("Deployment selesai. Menunggu log dari Heroku...")

    if choice == '2':
        subprocess.run(["heroku", "ps:scale", "web=1"])
    else:
        subprocess.run(["heroku", "ps:scale", "web=0"])
        subprocess.run(["heroku", "ps:scale", "worker=1"])
    
    print("Deployment dan setup selesai.")

def redeploy_app():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        git_configure()
        os.system("rm -rf .git")
        os.system("git init")
        subprocess.run(["heroku", "git:remote", "-a", nameapp])
        
        print("Deploy ke apa:")
        print("1. Node.js")
        print("2. PHP")
        choice = input("Masukkan pilihan Anda (default 1): ") or '1'

        buildpack = "heroku/nodejs" if choice == '1' else "heroku/php"

        subprocess.run(["heroku", "buildpacks:set", buildpack, "--app", nameapp])

        with open(".gitignore", "w") as f:
            if choice == '2':
                f.write("vendor/\n.env")
            else:
                f.write("node_modules/\n.git/") 
        
        os.system("git add .")
        subprocess.run(["git", "commit", "-m", "Redeploy"])
        subprocess.run(["git", "push", "heroku", "master", "--force"])
        print("Redeployment selesai. Menunggu log dari Heroku...")

        if choice == '2':
            subprocess.run(["heroku", "ps:scale", "web=1"])
        else:
            subprocess.run(["heroku", "ps:scale", "web=0"])
            subprocess.run(["heroku", "ps:scale", "worker=1"])

        print("Redeployment dan setup selesai.")

def add_buildpack():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        buildpacks = [
            'https://github.com/mcollina/heroku-buildpack-imagemagick.git',
            'https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git',
            'https://github.com/clhuang/heroku-buildpack-webp-binaries.git'
        ]
        for buildpack in buildpacks:
            subprocess.run(["heroku", "buildpacks:add", "--index", "1", buildpack, "--app", nameapp])
            print(f"Buildpack {buildpack} telah ditambahkan ke aplikasi {nameapp}.")
        redeploy_app()
def handle_command(command):
    commands = {
        "del_app": delete_app_by_name,
        "del_all_app": delete_all_apps,
        "c_dynos": check_dynos,
        "restart": restart_dynos,
        "restart_all": restart_all_dynos,
        "change_dynos": change_dyno_type,
        "change_dynos_all": change_all_dyno_types,
        "logs": view_logs,
        "deploy": deploy_app,
        "redeploy": redeploy_app,
        "addbuildpack": add_buildpack,
    }
    if command in commands:
        commands[command]()
    else:
        print("Perintah tidak valid.")

def main():
    parser = argparse.ArgumentParser(description="Manage Heroku applications.")
    parser.add_argument("cmd", help="Command to execute", nargs='?', default='help')
    
    args = parser.parse_args()
    if args.cmd == 'help':
        print("Perintah yang tersedia:")
        print("1. del_app - Hapus aplikasi berdasarkan nama")
        print("2. del_all_app - Hapus semua aplikasi")
        print("3. c_dynos - Cek sisa dynos")
        print("4. restart - Restart semua dynos dalam aplikasi")
        print("5. restart_all - Restart semua dynos dalam semua aplikasi")
        print("6. change_dynos - Ubah tipe dyno untuk satu aplikasi")
        print("7. change_dynos_all - Ubah tipe dyno untuk semua aplikasi")
        print("8. logs - Lihat logs aplikasi")
        print("9. deploy - Deploy aplikasi")
        print("10. redeploy - Deploy ulang")
        print("11. addbuildpack - Add buildpack")

    else:
        handle_command(args.cmd)

if __name__ == "__main__":
    main()

