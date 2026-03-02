import https from 'https';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');
const REPO_ZIP_URL = 'https://github.com/sickn33/antigravity-awesome-skills/archive/refs/heads/main.zip';

function followRedirects(url, dest) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);
        const request = (url) => {
            https.get(url, { headers: { 'User-Agent': 'antigravity-skills-app' } }, (res) => {
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                    request(res.headers.location);
                    return;
                }
                if (res.statusCode !== 200) {
                    reject(new Error(`Download failed with status ${res.statusCode}`));
                    return;
                }
                res.pipe(file);
                file.on('finish', () => { file.close(); resolve(); });
            }).on('error', (err) => { fs.unlink(dest, () => {}); reject(err); });
        };
        request(url);
    });
}

export default function refreshSkillsPlugin() {
    return {
        name: 'refresh-skills',
        configureServer(server) {
            server.middlewares.use('/api/refresh-skills', async (req, res) => {
                res.setHeader('Content-Type', 'application/json');

                const zipPath = path.join(ROOT_DIR, 'update.zip');
                const tempDir = path.join(ROOT_DIR, 'update_temp');

                try {
                    // 1. Download the ZIP
                    console.log('[Sync] Downloading latest skills from GitHub...');
                    await followRedirects(REPO_ZIP_URL, zipPath);

                    // 2. Extract with PowerShell (Windows) or unzip (Unix)
                    console.log('[Sync] Extracting archive...');
                    if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });

                    if (process.platform === 'win32') {
                        execSync(`powershell -Command "Expand-Archive -Path '${zipPath}' -DestinationPath '${tempDir}' -Force"`, { stdio: 'ignore' });
                    } else {
                        fs.mkdirSync(tempDir, { recursive: true });
                        execSync(`unzip -o "${zipPath}" -d "${tempDir}"`, { stdio: 'ignore' });
                    }

                    // 3. Copy skills folder + index
                    const extractedRoot = path.join(tempDir, 'antigravity-awesome-skills-main');
                    const srcSkills = path.join(extractedRoot, 'skills');
                    const srcIndex = path.join(extractedRoot, 'skills_index.json');
                    const destSkills = path.join(ROOT_DIR, 'skills');
                    const destIndex = path.join(ROOT_DIR, 'skills_index.json');

                    if (!fs.existsSync(srcSkills)) {
                        throw new Error('Skills folder not found in downloaded archive.');
                    }

                    // Replace skills folder
                    if (fs.existsSync(destSkills)) fs.rmSync(destSkills, { recursive: true, force: true });
                    copyFolderSync(srcSkills, destSkills);

                    // Replace index
                    if (fs.existsSync(srcIndex)) fs.copyFileSync(srcIndex, destIndex);

                    // 4. Re-run setup_web.js logic to update web-app/public
                    const webPublic = path.join(__dirname, 'public');
                    const webSkills = path.join(webPublic, 'skills');
                    const webIndex = path.join(webPublic, 'skills.json');

                    if (fs.existsSync(webSkills)) fs.rmSync(webSkills, { recursive: true, force: true });
                    copyFolderSync(destSkills, webSkills);
                    if (fs.existsSync(destIndex)) fs.copyFileSync(destIndex, webIndex);

                    // Count skills
                    const skillsData = JSON.parse(fs.readFileSync(webIndex, 'utf-8'));
                    const count = Array.isArray(skillsData) ? skillsData.length : 0;

                    console.log(`[Sync] ✅ Successfully synced ${count} skills!`);
                    res.end(JSON.stringify({ success: true, count }));

                } catch (err) {
                    console.error('[Sync] ❌ Failed:', err.message);
                    res.statusCode = 500;
                    res.end(JSON.stringify({ success: false, error: err.message }));
                } finally {
                    // Cleanup
                    if (fs.existsSync(zipPath)) fs.unlinkSync(zipPath);
                    if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
                }
            });
        }
    };
}

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) fs.mkdirSync(to, { recursive: true });
    for (const element of fs.readdirSync(from)) {
        const srcPath = path.join(from, element);
        const destPath = path.join(to, element);
        if (fs.lstatSync(srcPath).isFile()) {
            fs.copyFileSync(srcPath, destPath);
        } else {
            copyFolderSync(srcPath, destPath);
        }
    }
}
