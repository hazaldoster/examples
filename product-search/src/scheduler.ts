import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import ora from 'ora';

export async function setupCronJob(options: { file: string, interval: string }, apiKey: string) {
  const spinner = ora('Setting up scheduled task...').start();

  try {
    // Get absolute paths
    const scriptPath = path.resolve(__dirname, '..');
    const filePath = path.resolve(options.file);

    // Create the script to run
    const scriptContent = createCronScript(scriptPath, options, apiKey);
    const scriptFilePath = path.join(scriptPath, 'run-scheduled-task.sh');

    fs.writeFileSync(scriptFilePath, scriptContent);
    fs.chmodSync(scriptFilePath, '755'); // Make executable

    spinner.succeed('Created task script at ' + scriptFilePath);

    // Add to crontab
    spinner.start('Adding task to crontab...');

    const cronCommand = `(crontab -l 2>/dev/null || echo "") | grep -v "${scriptFilePath}" | cat - <(echo "${options.interval} ${scriptFilePath}") | crontab -`;

    const process = spawn('bash', ['-c', cronCommand]);

    process.on('close', (code) => {
      if (code === 0) {
        spinner.succeed(`Task scheduled! Will run: ${options.interval}`);
      } else {
        spinner.fail('Failed to add cron job. You may need to add it manually.');
        console.log(`Add this line to your crontab: ${options.interval} ${scriptFilePath}`);
      }
    });

  } catch (error) {
    spinner.fail('Error setting up cron job');
    console.error('Error details:', error);
  }
}

export async function removeCronJob(options: { deleteScript: boolean }) {
  const spinner = ora('Removing scheduled task...').start();

  try {
    // Find the script path
    const scriptPath = path.resolve(__dirname, '..');
    const scriptFilePath = path.join(scriptPath, 'run-scheduled-task.sh');

    if (!fs.existsSync(scriptFilePath)) {
      spinner.info('No scheduled task script found. Nothing to remove.');
      return;
    }

    // Remove from crontab
    spinner.text = 'Removing task from crontab...';

    const cronCommand = `(crontab -l 2>/dev/null || echo "") | grep -v "${scriptFilePath}" | crontab -`;

    const process = spawn('bash', ['-c', cronCommand]);

    process.on('close', (code) => {
      if (code === 0) {
        spinner.succeed('Task removed from crontab');

        // Delete the script file if requested
        if (options.deleteScript) {
          try {
            fs.unlinkSync(scriptFilePath);
            console.log(`Script file deleted: ${scriptFilePath}`);
          } catch (error) {
            console.error(`Failed to delete script file: ${error}`);
          }
        } else {
          console.log(`Script file remains at: ${scriptFilePath}`);
          console.log('You can delete it manually or use --delete-script flag next time');
        }
      } else {
        spinner.fail('Failed to remove cron job. You may need to remove it manually.');
        console.log('To manually remove, run: crontab -e');
        console.log(`And remove the line containing: ${scriptFilePath}`);
      }
    });

  } catch (error) {
    spinner.fail('Error removing cron job');
    console.error('Error details:', error);
  }
}

// Helper function to create the shell script content
function createCronScript(basePath: string, options: { file: string }, apiKey: string) {
  const nodeExecPath = process.execPath; // Path to the current Node.js executable
  const indexPath = path.join(basePath, 'dist/index.js');

  let command = `${nodeExecPath} ${indexPath} refresh --file "${options.file}"`;

  return `#!/bin/bash
# Auto-generated script for product finder scheduled task
# Created: ${new Date().toISOString()}

# Change to the application directory
cd "${basePath}"
export HYPERBROWSER_API_KEY=${apiKey}

# Run the command
${command} >> "${basePath}/scheduled-run.log" 2>&1
`;
} 