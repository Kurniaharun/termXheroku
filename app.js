const { execSync } = require('child_process');
const readline = require('readline');

// Fungsi untuk mengkonfigurasi Git
function gitConfigure() {
    try {
        execSync('git config user.name');
    } catch (error) {
        execSync('git config --global user.name "vnotvirus"');
        execSync('git config --global user.email "itsv@rill.cuy"');
    }
}

// Fungsi untuk mendapatkan daftar aplikasi
function listApps() {
    const result = execSync('heroku apps').toString();
    const apps = result.split('\n').filter(line => line && !line.startsWith('=')).map(line => line.split(' ')[0]);
    console.log('Daftar aplikasi Heroku:');
    apps.forEach((app, idx) => console.log(`${idx + 1}. ${app}`));
    return apps;
}

// Fungsi untuk memilih aplikasi
function chooseApp(apps) {
    const choice = parseInt(prompt('Pilih nomor aplikasi: '));
    if (choice >= 1 && choice <= apps.length) {
        return apps[choice - 1];
    } else {
        console.log('Nomor aplikasi tidak valid.');
        return null;
    }
}

// Fungsi untuk menjalankan perintah Heroku
function runHerokuCommand(command) {
    execSync(command, { stdio: 'inherit' });
}

// Fungsi untuk menampilkan menu
function displayMenu() {
    console.log('Pilih fitur yang ingin digunakan:');
    console.log('1. Deploy aplikasi');
    console.log('2. Hapus aplikasi berdasarkan nama');
    console.log('3. Hapus semua aplikasi');
    console.log('4. Cek dynos');
    console.log('5. Restart dynos');
    console.log('6. Ubah tipe dyno');
    console.log('7. Lihat logs aplikasi');
    console.log('8. Keluar');
}

// Fungsi untuk meminta input dari pengguna
function prompt(message) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(message, (answer) => {
            rl.close();
            resolve(answer);
        });
    });
}

// Fungsi utama untuk menjalankan menu
async function main() {
    while (true) {
        displayMenu();
        const choice = await prompt('Masukkan pilihan Anda: ');

        switch (choice) {
            case '1':
                const appName = await prompt('NAMA APP?: ') + '-app';
                gitConfigure();
                execSync('rm -rf .git');
                runHerokuCommand(`heroku create ${appName}`);
                execSync('git init');
                runHerokuCommand(`heroku git:remote -a ${appName}`);

                console.log('Deploy ke apa:');
                console.log('1. Node.js');
                console.log('2. PHP');
                const buildChoice = await prompt('Masukkan pilihan Anda (default 1): ') || '1';
                const buildpack = buildChoice === '1' ? 'heroku/nodejs' : 'heroku/php';

                runHerokuCommand(`heroku buildpacks:set ${buildpack} --app ${appName}`);
                execSync('echo "node_modules/" > .gitignore');

                execSync('git add .');
                runHerokuCommand('git commit -m "Initial commit"');
                runHerokuCommand('git push heroku master');

                console.log('Deployment selesai. Menunggu log dari Heroku...');
                break;

            case '2':
                const appsToDelete = listApps();
                const appToDelete = chooseApp(appsToDelete);
                if (appToDelete) {
                    runHerokuCommand(`heroku apps:destroy --app ${appToDelete} --confirm ${appToDelete}`);
                    console.log(`Aplikasi ${appToDelete} telah dihapus.`);
                }
                break;

            case '3':
                const allApps = listApps();
                for (const app of allApps) {
                    runHerokuCommand(`heroku apps:destroy --app ${app} --confirm ${app}`);
                    console.log(`Aplikasi ${app} telah dihapus.`);
                }
                break;

            case '4':
                const appsCheck = listApps();
                const appToCheck = chooseApp(appsCheck);
                if (appToCheck) {
                    runHerokuCommand(`heroku ps --app ${appToCheck}`);
                }
                break;

            case '5':
                const appsRestart = listApps();
                const appToRestart = chooseApp(appsRestart);
                if (appToRestart) {
                    runHerokuCommand(`heroku ps:restart --app ${appToRestart}`);
                    console.log(`Dynos pada aplikasi ${appToRestart} telah di-restart.`);
                }
                break;

            case '6':
                const appsChangeDyno = listApps();
                const appToChange = chooseApp(appsChangeDyno);
                if (appToChange) {
                    const dynoType = await prompt('Masukkan tipe dyno (eco/basic): ').trim().toLowerCase();
                    const typeCode = dynoType === 'eco' ? 'eco' : dynoType === 'basic' ? 'standard-1x' : null;

                    if (typeCode) {
                        runHerokuCommand(`heroku ps:type ${typeCode} --app ${appToChange}`);
                        console.log(`Tipe dyno pada aplikasi ${appToChange} telah diubah menjadi ${dynoType}.`);
                    } else {
                        console.log('Tipe dyno tidak valid.');
                    }
                }
                break;

            case '7':
                const appsLogs = listApps();
                const appToViewLogs = chooseApp(appsLogs);
                if (appToViewLogs) {
                    runHerokuCommand(`heroku logs --tail --app ${appToViewLogs}`);
                }
                break;

            case '8':
                console.log('Keluar...');
                return;

            default:
                console.log('Pilihan tidak valid.');
                break;
        }
    }
}

main();