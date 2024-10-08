import os
import subprocess
import sys

def install_required_packages():
    """Auto-install necessary Python packages if not already installed."""
    required_packages = ['requests']  # Tambahkan modul lain yang perlu diinstal secara otomatis

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

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

def delete_app():
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
        type_code = 'eco' if dyno_type == 'eco' else 'standard-1x' if dyno_type == 'basic' else None
        
        if type_code:
            subprocess.run(["heroku", "ps:type", type_code, "--app", nameapp])
            print(f"Tipe dyno pada aplikasi {nameapp} telah diubah menjadi {dyno_type}.")
        else:
            print("Tipe dyno tidak valid.")

def view_logs():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        subprocess.run(["heroku", "logs", "--tail", "--app", nameapp])

def create_app():
    nameapp = input("Nama aplikasi baru: ") + "-app"
    git_configure()
    os.system("rm -rf .git")
    subprocess.run(["heroku", "create", nameapp])
    os.system("git init")
    subprocess.run(["heroku", "git:remote", "-a", nameapp])
    print(f"Aplikasi {nameapp} telah dibuat.")

def deploy_app():
    nameapp = input("Nama aplikasi: ") + "-app"
    git_configure()
    os.system("rm -rf .git")
    subprocess.run(["heroku", "create", nameapp])
    os.system("git init")
    subprocess.run(["heroku", "git:remote", "-a", nameapp])
    
    buildpacks = [
        "heroku/nodejs", 
        "heroku/php", 
        "heroku/python"
    ]

    print("Pilih buildpack untuk deploy:")
    for idx, bp in enumerate(buildpacks, start=1):
        print(f"{idx}. {bp}")
    
    choice = int(input("Pilih buildpack: ")) - 1
    selected_buildpack = buildpacks[choice]

    subprocess.run(["heroku", "buildpacks:set", selected_buildpack, "--app", nameapp])
    with open(".gitignore", "w") as f:
        f.write("node_modules/\n" if "nodejs" in selected_buildpack else "vendor/\n.env")
    
    os.system("git add .")
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    subprocess.run(["git", "push", "heroku", "master"])

    print("Deployment selesai. Menunggu log dari Heroku...")

    if input("Apakah Anda ingin menyalakan dynos untuk aplikasi ini? (Y/N): ").strip().lower() == 'y':
        dyno_type = input("Masukkan tipe dyno (eco/basic): ").strip().lower()
        type_code = 'eco' if dyno_type == 'eco' else 'standard-1x'
        subprocess.run(["heroku", "ps:type", type_code, "--app", nameapp])
        print(f"Dynos pada aplikasi {nameapp} telah diatur ke {dyno_type}.")

def redeploy_app():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        git_configure()
        os.system("rm -rf .git")
        os.system("git init")
        subprocess.run(["heroku", "git:remote", "-a", nameapp])
        
        print("Redeploying app...")
        os.system("git add .")
        subprocess.run(["git", "commit", "-m", "Redeploy"])
        subprocess.run(["git", "push", "heroku", "master", "--force"])
        print("Redeployment selesai.")

def add_buildpack():
    apps = list_apps()
    nameapp = choose_app(apps)
    if nameapp:
        buildpacks = [
            'https://github.com/mcollina/heroku-buildpack-imagemagick.git',
            'https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git',
            'https://github.com/clhuang/heroku-buildpack-webp-binaries.git',
            'heroku/nodejs',
            'heroku/php',
            'heroku/python'
        ]
        for buildpack in buildpacks:
            subprocess.run(["heroku", "buildpacks:add", "--index", "1", buildpack, "--app", nameapp])
            print(f"Buildpack {buildpack} telah ditambahkan ke aplikasi {nameapp}.")
        redeploy_app()

def display_menu():
    print("Heroku Tools Manager")
    print("Version: 1.0 - Stable")
    print("\nPilih Opsi:")
    print("1. Buat Aplikasi Baru")
    print("2. Deploy Aplikasi")
    print("3. Redeploy Aplikasi")
    print("4. Hapus Aplikasi")
    print("5. Hapus Semua Aplikasi")
    print("6. Cek Dynos")
    print("7. Restart Dynos")
    print("8. Restart Semua Dynos")
    print("9. Lihat Log")
    print("10. Tambah Buildpack")
    print("11. Keluar")

def handle_command(command):
    commands = {
        "1": create_app,
        "2": deploy_app,
        "3": redeploy_app,
        "4": delete_app,
        "5": delete_all_apps,
        "6": check_dynos,
        "7": restart_dynos,
        "8": restart_all_dynos,
        "9": view_logs,
        "10": add_buildpack,
    }
    if command in commands:
        commands[command]()
    elif command == '11':
        print("Keluar dari program.")
        exit()
    else:
        print("Perintah tidak valid.")

def main():
    install_required_packages()
    while True:
        os.system("clear")
        print("=== Heroku Panel ===")
        display_menu()
        choice = input("Masukkan pilihan Anda: ")
        handle_command(choice)

if __name__ == "__main__":
    main()