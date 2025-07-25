#!/usr/bin/env node
/**
 * Financial Analytics Hub - Frontend Health Check Script
 * This script verifies the frontend service health and diagnoses issues.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// Configuration
const FRONTEND_PORT = 3000;
const BACKEND_PORT = 8001;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;
const FRONTEND_URL = `http://localhost:${FRONTEND_PORT}`;

// ANSI Colors
const Colors = {
    GREEN: '\x1b[92m',
    RED: '\x1b[91m',
    YELLOW: '\x1b[93m',
    BLUE: '\x1b[94m',
    PURPLE: '\x1b[95m',
    CYAN: '\x1b[96m',
    ENDC: '\x1b[0m',
    BOLD: '\x1b[1m'
};

// Utility functions
function printHeader() {
    console.log(`${Colors.PURPLE}${'='.repeat(60)}${Colors.ENDC}`);
    console.log(`${Colors.PURPLE}${Colors.BOLD}  Financial Analytics Hub - Frontend Health Check${Colors.ENDC}`);
    console.log(`${Colors.PURPLE}${'='.repeat(60)}${Colors.ENDC}\n`);
}

function printSuccess(message) {
    console.log(`${Colors.GREEN}✅ [SUCCESS]${Colors.ENDC} ${message}`);
}

function printError(message) {
    console.log(`${Colors.RED}❌ [ERROR]${Colors.ENDC} ${message}`);
}

function printWarning(message) {
    console.log(`${Colors.YELLOW}⚠️  [WARNING]${Colors.ENDC} ${message}`);
}

function printInfo(message) {
    console.log(`${Colors.BLUE}ℹ️  [INFO]${Colors.ENDC} ${message}`);
}

function printStep(message) {
    console.log(`${Colors.CYAN}🔍 [STEP]${Colors.ENDC} ${message}`);
}

// Health check functions
async function checkNodeVersion() {
    printStep('Checking Node.js version...');
    
    try {
        const { stdout } = await execAsync('node --version');
        const version = stdout.trim();
        const majorVersion = parseInt(version.substring(1).split('.')[0]);
        
        if (majorVersion >= 18) {
            printSuccess(`Node.js version: ${version} ✓`);
            return true;
        } else {
            printError(`Node.js version ${version} is too old. Requires v18 or higher.`);
            return false;
        }
    } catch (error) {
        printError(`Node.js not found: ${error.message}`);
        return false;
    }
}

async function checkPackageManager() {
    printStep('Checking package manager (pnpm)...');
    
    try {
        const { stdout } = await execAsync('pnpm --version');
        const version = stdout.trim();
        printSuccess(`pnpm version: ${version} ✓`);
        return true;
    } catch (error) {
        printWarning('pnpm not found. Checking for npm...');
        
        try {
            const { stdout } = await execAsync('npm --version');
            const version = stdout.trim();
            printWarning(`Using npm version: ${version} (pnpm recommended)`);
            return true;
        } catch (npmError) {
            printError('Neither pnpm nor npm found');
            return false;
        }
    }
}

async function checkPackageJson() {
    printStep('Checking package.json...');
    
    const packageJsonPath = path.join(process.cwd(), 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
        printError('package.json not found');
        return false;
    }
    
    try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        
        printSuccess('package.json found ✓');
        
        // Check for essential dependencies
        const requiredDeps = ['react', 'next'];
        const missingDeps = [];
        
        requiredDeps.forEach(dep => {
            if (!packageJson.dependencies || !packageJson.dependencies[dep]) {
                missingDeps.push(dep);
            }
        });
        
        if (missingDeps.length > 0) {
            printError(`Missing dependencies: ${missingDeps.join(', ')}`);
            return false;
        }
        
        printSuccess('Essential dependencies found ✓');
        return true;
    } catch (error) {
        printError(`Error reading package.json: ${error.message}`);
        return false;
    }
}

async function checkNodeModules() {
    printStep('Checking node_modules...');
    
    const nodeModulesPath = path.join(process.cwd(), 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath)) {
        printWarning('node_modules not found - dependencies need to be installed');
        printInfo('Run: pnpm install');
        return false;
    }
    
    // Check if essential packages are installed
    const essentialPackages = ['react', 'next'];
    const missingPackages = [];
    
    essentialPackages.forEach(pkg => {
        const pkgPath = path.join(nodeModulesPath, pkg);
        if (!fs.existsSync(pkgPath)) {
            missingPackages.push(pkg);
        }
    });
    
    if (missingPackages.length > 0) {
        printError(`Missing packages in node_modules: ${missingPackages.join(', ')}`);
        printInfo('Run: pnpm install');
        return false;
    }
    
    printSuccess('node_modules appears healthy ✓');
    return true;
}

async function checkPortAvailability() {
    printStep(`Checking if port ${FRONTEND_PORT} is available...`);
    
    return new Promise((resolve) => {
        const server = http.createServer();
        
        server.listen(FRONTEND_PORT, 'localhost', () => {
            server.close(() => {
                printSuccess(`Port ${FRONTEND_PORT} is available ✓`);
                resolve(true);
            });
        });
        
        server.on('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                printWarning(`Port ${FRONTEND_PORT} is already in use`);
                printInfo('This might be the frontend service already running');
                resolve(false);
            } else {
                printError(`Error checking port ${FRONTEND_PORT}: ${error.message}`);
                resolve(false);
            }
        });
    });
}

async function checkFrontendService() {
    printStep('Checking if frontend service is running...');
    
    return new Promise((resolve) => {
        const req = http.get(FRONTEND_URL, (res) => {
            if (res.statusCode === 200) {
                printSuccess('Frontend service is running and responding ✓');
                resolve(true);
            } else {
                printWarning(`Frontend service responded with status: ${res.statusCode}`);
                resolve(false);
            }
        });
        
        req.on('error', (error) => {
            if (error.code === 'ECONNREFUSED') {
                printError('Frontend service is not running');
                printInfo('Start with: pnpm dev');
            } else {
                printError(`Error connecting to frontend: ${error.message}`);
            }
            resolve(false);
        });
        
        req.setTimeout(5000, () => {
            printError('Frontend service connection timeout');
            resolve(false);
        });
    });
}

async function checkBackendConnectivity() {
    printStep('Testing backend connectivity from frontend perspective...');
    
    const testEndpoints = [
        '/health',
        '/api/status',
        '/api/crypto/trending'
    ];
    
    const results = {};
    
    for (const endpoint of testEndpoints) {
        const url = `${BACKEND_URL}${endpoint}`;
        
        try {
            await new Promise((resolve) => {
                const req = http.get(url, (res) => {
                    if (res.statusCode === 200) {
                        printSuccess(`${endpoint}: OK`);
                        results[endpoint] = true;
                        resolve();
                    } else {
                        printWarning(`${endpoint}: Status ${res.statusCode}`);
                        results[endpoint] = false;
                        resolve();
                    }
                });
                
                req.on('error', (error) => {
                    printError(`${endpoint}: ${error.message}`);
                    results[endpoint] = false;
                    resolve();
                });
                
                req.setTimeout(10000, () => {
                    printError(`${endpoint}: Timeout`);
                    results[endpoint] = false;
                    resolve();
                });
            });
        } catch (error) {
            printError(`${endpoint}: ${error.message}`);
            results[endpoint] = false;
        }
    }
    
    return results;
}

async function checkBuildCapability() {
    printStep('Testing build capability...');
    
    try {
        printInfo('Running build check (this may take a moment)...');
        
        const { stdout, stderr } = await execAsync('pnpm build --dry-run || npm run build --dry-run || echo "Build check skipped"', {
            timeout: 30000
        });
        
        if (stdout.includes('Build check skipped')) {
            printWarning('Build check skipped - build script may not support dry-run');
            return true;
        }
        
        if (stderr && stderr.includes('error')) {
            printError('Build test failed');
            printInfo('There may be compilation errors in the code');
            return false;
        }
        
        printSuccess('Build capability check passed ✓');
        return true;
    } catch (error) {
        printWarning(`Build check failed: ${error.message}`);
        printInfo('This might indicate compilation issues');
        return false;
    }
}

async function checkEnvironmentVariables() {
    printStep('Checking environment variables...');
    
    const envFiles = ['.env', '.env.local', '.env.development'];
    let envFileFound = false;
    
    envFiles.forEach(file => {
        if (fs.existsSync(file)) {
            printSuccess(`Environment file found: ${file} ✓`);
            envFileFound = true;
        }
    });
    
    if (!envFileFound) {
        printWarning('No environment files found');
        printInfo('Consider creating .env.local for environment variables');
    }
    
    // Check for common Next.js environment variables
    const nextConfig = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
    if (nextConfig) {
        printSuccess('API URL configuration found ✓');
    } else {
        printWarning('No API URL configuration found');
        printInfo('Consider setting NEXT_PUBLIC_API_URL or API_URL');
    }
    
    return true;
}

async function generateReport(results) {
    console.log();
    console.log(`${Colors.PURPLE}${Colors.BOLD}${'='.repeat(60)}${Colors.ENDC}`);
    console.log(`${Colors.PURPLE}${Colors.BOLD}  FRONTEND HEALTH REPORT${Colors.ENDC}`);
    console.log(`${Colors.PURPLE}${Colors.BOLD}${'='.repeat(60)}${Colors.ENDC}`);
    console.log();
    
    // Overall status
    const overallHealthy = Object.values(results).every(result => 
        typeof result === 'boolean' ? result : Object.values(result).every(Boolean)
    );
    
    if (overallHealthy) {
        console.log(`${Colors.GREEN}${Colors.BOLD}🎉 OVERALL STATUS: HEALTHY${Colors.ENDC}`);
    } else {
        console.log(`${Colors.RED}${Colors.BOLD}❌ OVERALL STATUS: ISSUES DETECTED${Colors.ENDC}`);
    }
    
    console.log();
    
    // Detailed status
    const statusItems = [
        ['Node.js Version', results.nodeVersion ? '✅' : '❌'],
        ['Package Manager', results.packageManager ? '✅' : '❌'],
        ['Package Configuration', results.packageJson ? '✅' : '❌'],
        ['Dependencies', results.nodeModules ? '✅' : '❌'],
        ['Port Availability', results.portAvailable ? '✅' : '⚠️'],
        ['Frontend Service', results.frontendRunning ? '✅' : '❌'],
        ['Backend Connectivity', Object.values(results.backendConnectivity || {}).some(Boolean) ? '✅' : '❌'],
        ['Build Capability', results.buildCapable ? '✅' : '⚠️']
    ];
    
    statusItems.forEach(([item, status]) => {
        console.log(`${item.padEnd(20)} ${status}`);
    });
    
    // Backend connectivity details
    if (results.backendConnectivity) {
        console.log(`\n${Colors.BLUE}Backend Connectivity:${Colors.ENDC}`);
        Object.entries(results.backendConnectivity).forEach(([endpoint, status]) => {
            const statusIcon = status ? '✅' : '❌';
            console.log(`  ${endpoint.padEnd(25)} ${statusIcon}`);
        });
    }
    
    // Recommendations
    console.log(`\n${Colors.PURPLE}Recommendations:${Colors.ENDC}`);
    
    if (!results.nodeVersion) {
        console.log('  • Update Node.js to version 18 or higher');
    }
    
    if (!results.packageManager) {
        console.log('  • Install pnpm: npm install -g pnpm');
    }
    
    if (!results.nodeModules) {
        console.log('  • Install dependencies: pnpm install');
    }
    
    if (!results.frontendRunning) {
        console.log('  • Start frontend service: pnpm dev');
    }
    
    if (!Object.values(results.backendConnectivity || {}).some(Boolean)) {
        console.log('  • Ensure backend service is running on port 8001');
        console.log('  • Check backend health with: python services/backend/check-backend.py');
    }
    
    if (!results.buildCapable) {
        console.log('  • Fix compilation errors before deployment');
        console.log('  • Run: pnpm build to see detailed errors');
    }
}

// Main execution
async function main() {
    printHeader();
    
    const results = {};
    
    // Step 1: Check Node.js version
    results.nodeVersion = await checkNodeVersion();
    
    // Step 2: Check package manager
    results.packageManager = await checkPackageManager();
    
    // Step 3: Check package.json
    results.packageJson = await checkPackageJson();
    
    // Step 4: Check node_modules
    results.nodeModules = await checkNodeModules();
    
    // Step 5: Check environment variables
    results.envVariables = await checkEnvironmentVariables();
    
    // Step 6: Check port availability
    results.portAvailable = await checkPortAvailability();
    
    // Step 7: Check if frontend service is running
    results.frontendRunning = await checkFrontendService();
    
    // Step 8: Test backend connectivity
    results.backendConnectivity = await checkBackendConnectivity();
    
    // Step 9: Check build capability
    results.buildCapable = await checkBuildCapability();
    
    // Step 10: Generate comprehensive report
    await generateReport(results);
    
    // Exit with appropriate code
    const success = results.nodeVersion && results.packageManager && results.packageJson;
    process.exit(success ? 0 : 1);
}

// Handle errors
process.on('unhandledRejection', (error) => {
    printError(`Unhandled error: ${error.message}`);
    process.exit(1);
});

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        printError(`Script error: ${error.message}`);
        process.exit(1);
    });
} 