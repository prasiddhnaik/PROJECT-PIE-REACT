import json
import os
from datetime import datetime
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    logger.info("Cryptography module imported successfully")
except ImportError:
    logger.error("Cryptography module not found. Install with: pip install cryptography")
    print("Error: Cryptography module not found. Install with: pip install cryptography")
    sys.exit(1)

def backup_api_keys():
    """Backup API keys with encryption"""
    
    # Generate encryption key
    encryption_key = Fernet.generate_key()
    cipher = Fernet(encryption_key)
    
    # Collect all keys
    keys_data = {
        'backup_date': datetime.now().isoformat(),
        'keys': {
            'POLYGON_KEY': os.getenv('POLYGON_KEY', 'SavZMeuTDTxjWJuFzBO6zES7mBFK68RJ'),
            'MARKETSTACK_KEY': os.getenv('MARKETSTACK_KEY', '10ca00f0992844c25ea3722d5913825c'),
            'ALPHA_VANTAGE_KEY': os.getenv('ALPHA_VANTAGE_KEY', '0FHER7X1A6WKLP5N'),
            'TWELVE_DATA_KEY': os.getenv('TWELVE_DATA_KEY', '2df82f24652f4fb08d90fcd537a97e9c'),
            'FINNHUB_KEY': os.getenv('FINNHUB_KEY', '')
        }
    }
    
    # Encrypt and save
    encrypted_data = cipher.encrypt(json.dumps(keys_data).encode())
    
    # Create backup directory if it doesn't exist
    backup_dir = 'key_backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Save encrypted backup with timestamp
    backup_filename = f"{backup_dir}/api_keys_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
    with open(backup_filename, 'wb') as f:
        f.write(encrypted_data)
    
    # Save encryption key separately (keep this safe!)
    key_filename = f"{backup_dir}/backup_key_{datetime.now().strftime('%Y%m%d_%H%M%S')}.key"
    with open(key_filename, 'wb') as f:
        f.write(encryption_key)
    
    logger.info(f"✅ API keys backed up successfully to {backup_filename}")
    print(f"✅ API keys backed up successfully to {backup_filename}")
    print(f"⚠️  Keep '{key_filename}' safe - you need it to restore keys!")

def restore_api_keys(backup_file, key_file):
    """Restore API keys from backup"""
    
    try:
        # Read encryption key
        with open(key_file, 'rb') as f:
            encryption_key = f.read()
        
        # Read encrypted data
        with open(backup_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt data
        cipher = Fernet(encryption_key)
        decrypted_data = cipher.decrypt(encrypted_data)
        keys_data = json.loads(decrypted_data.decode())
        
        # Print restored keys
        print("🔑 Restored API Keys:")
        print("=" * 50)
        print(f"Backup Date: {keys_data['backup_date']}")
        print("\nAPI Keys:")
        
        for service, key in keys_data['keys'].items():
            if key:
                # Show only last 4 characters
                masked_key = f"{'*' * (len(key) - 4)}{key[-4:]}" if len(key) > 4 else "****"
                print(f"  {service}: {masked_key}")
            else:
                print(f"  {service}: Not configured")
        
        # Option to create .env file
        create_env = input("\nDo you want to create a .env file with these keys? (y/n): ")
        if create_env.lower() == 'y':
            with open('.env', 'w') as f:
                for service, key in keys_data['keys'].items():
                    if key:
                        f.write(f"{service}={key}\n")
            print("✅ .env file created successfully!")
        
        return True
    except Exception as e:
        logger.error(f"Error restoring keys: {e}")
        print(f"❌ Error restoring keys: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup or restore API keys')
    parser.add_argument('--restore', action='store_true', help='Restore keys from backup')
    parser.add_argument('--backup-file', help='Backup file to restore from')
    parser.add_argument('--key-file', help='Key file to use for decryption')
    
    args = parser.parse_args()
    
    if args.restore:
        if not args.backup_file or not args.key_file:
            print("Error: --backup-file and --key-file are required for restore")
            sys.exit(1)
        
        restore_api_keys(args.backup_file, args.key_file)
    else:
        backup_api_keys() 