// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Congratulations, your extension "lingxi-code-diagnoser" is now active!');

    // ================= 通用诊断函数 =================
    function runDiagnosis(diagnosisType, useDoubao = false) {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('请先打开要诊断的代码文件');
            return;
        }

        const document = editor.document;
        const filePath = document.uri.fsPath;

        console.log('File to diagnose:', filePath);
        console.log('Document language:', document.languageId);

        // 获取配置
        const config = vscode.workspace.getConfiguration('lingxi-code-diagnoser');
        let pythonPath = config.get('pythonPath');
        let workingDir = config.get('workingDirectory');

        // 自动定位工作目录
        if (!workingDir || workingDir.trim() === '') {
            // 优先使用 VS Code 工作区根目录
            const workspaceFolder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
            if (workspaceFolder) {
                workingDir = workspaceFolder.uri.fsPath;
            } else {
                // 如果没有工作区，尝试从插件目录定位 lingxi.py
                const pluginPath = context.extensionPath;
                workingDir = path.join(pluginPath, '..'); // 插件目录的上一级是项目根目录
            }
        }

        // 检查 lingxi.py 是否存在
        const lingxiPath = path.join(workingDir, 'lingxi.py');
        if (!fs.existsSync(lingxiPath)) {
            vscode.window.showErrorMessage(`未找到 lingxi.py，工作目录可能错误: ${workingDir}`);
            return;
        }

        // 构造命令参数
        const args = [];
        args.push(path.join(workingDir, 'vscode_plugin', 'diagnose_code.py'));
        args.push(filePath);
        args.push('-t');
        args.push(diagnosisType);

        // 调试信息
        console.log('Python Path:', pythonPath);
        console.log('Working Dir:', workingDir);
        console.log('Arguments:', args.join(' '));

        if (useDoubao) {
            args.push('-b');
            args.push('豆包');
        }

        if (diagnosisType === 'comments') {
            args.push('-a'); // 自动应用注释
        }

        console.log('Python Path:', pythonPath);
        console.log('Working Dir:', workingDir);
        console.log('Arguments:', args.join(' '));

        vscode.window.showInformationMessage(`正在使用 Python ${pythonPath} 进行诊断...`);

        // 检查 Python 是否可执行
        if (!pythonPath || pythonPath.trim() === '') {
            vscode.window.showErrorMessage('Python 路径未配置，请在设置中设置 lingxi-code-diagnoser.pythonPath');
            return;
        }

        // 执行诊断
        console.log('Starting child process...');
        const childProcess = spawn(pythonPath, args, {
            cwd: workingDir,
            encoding: 'utf8',
            env: {
                ...process.env,
                PYTHONIOENCODING: 'utf-8',
                PYTHONUTF8: '1'
            }
        });

        let stdoutData = '';
        let stderrData = '';

        childProcess.stdout.on('data', (data) => {
            stdoutData += data.toString();
        });

        childProcess.stderr.on('data', (data) => {
            stderrData += data.toString();
        });

        childProcess.on('close', (code) => {
            if (code === 0) {
                const outputWindow = vscode.window.createOutputChannel('Lingxi Code Diagnoser');
                outputWindow.show();
                outputWindow.appendLine('=== 灵犀代码诊断助手 ===');
                outputWindow.appendLine('诊断结果:');
                outputWindow.appendLine(stdoutData);
                vscode.window.showInformationMessage(`诊断完成！请查看 "Lingxi Code Diagnoser" 输出窗口`);
            } else {
                console.error('stderr:', stderrData);
                console.error('stdout:', stdoutData);
                console.error('exit code:', code);
                vscode.window.showErrorMessage(`诊断脚本运行失败 (退出码: ${code}): ${stderrData || stdoutData}`);
            }
        });

        childProcess.on('error', (err) => {
            console.error('Error:', err);
            console.error('Error message:', err.message);
            console.error('Error code:', err.code);
            console.error('Error errno:', err.errno);
            vscode.window.showErrorMessage(`启动诊断进程失败: ${err.message}`);
        });
    }

    // ================= 命令注册 =================

    // 诊断运行时错误
    let diagnoseCode = vscode.commands.registerCommand('lingxi-code-diagnoser.diagnoseCode', () => {
        runDiagnosis('errors');
    });

    // 添加单行注释
    let addComments = vscode.commands.registerCommand('lingxi-code-diagnoser.addComments', () => {
        runDiagnosis('comments');
    });

    // 使用豆包诊断
    let diagnoseWithDoubao = vscode.commands.registerCommand('lingxi-code-diagnoser.diagnoseWithDoubao', () => {
        runDiagnosis('errors', true);
    });

    context.subscriptions.push(diagnoseCode, addComments, diagnoseWithDoubao);
}

function deactivate() {
    console.log('lingxi-code-diagnoser extension deactivated');
}

module.exports = {
    activate,
    deactivate
};
