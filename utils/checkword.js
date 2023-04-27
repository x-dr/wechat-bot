import * as fs from 'fs'
// import {fileURLToPath} from 'url'
import path from 'path'
const __dirname = path.resolve();

// 获取当前目录下的所有txt文件
// console.log(__dirname);
// console.log(__filename);
const files = fs.readdirSync(`${__dirname}/utils/word/`)
    .filter((file) => file.endsWith('.txt'))
// console.log(files);

export const containsTextFileLine =async(text, filePaths=files)=> {
    // console.log(filePaths);
    for (let i = 0; i < filePaths.length; i++) {
        const lines = fs.readFileSync(`utils/word/${filePaths[i]}`, 'utf-8').split(/\r?\n/);
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line && text.includes(line)) {
                //   return true;
                //   return text.replace(line, '***');
                text = text.replace(new RegExp(line, 'g'), '***');
            }
        }
    }
    //   return false;
    return text;
}


