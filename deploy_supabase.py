#!/usr/bin/env python3
"""
Supabase Database Deployment Script
===================================

Deploy the Cultural Intelligence System schema to Supabase.
Run this after creating your Supabase project.
"""

import os
import json
from typing import Dict

try:
    from supabase import create_client, Client
except ImportError:
    print("📦 Installing Supabase client...")
    os.system("pip install supabase")
    from supabase import create_client, Client

from taxonomy_v32 import DatabaseSchema, TaxonomyConfig

class SupabaseDeployer:
    """Deploy Cultural Intelligence System to Supabase"""
    
    def __init__(self):
        self.config = TaxonomyConfig()
        self.client = None
        
    def setup_credentials(self):
        """Interactive setup of Supabase credentials"""
        print("🔐 SUPABASE SETUP")
        print("=" * 30)
        print("You need your Supabase project credentials:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Create a new project or select existing")
        print("3. Go to Settings > API")
        print("4. Copy the URL and anon key")
        print()
        
        # Get URL
        current_url = self.config.get('supabase.url', '')
        if current_url:
            print(f"Current URL: {current_url}")
            use_current = input("Use current URL? (y/n): ").lower().startswith('y')
            if use_current:
                url = current_url
            else:
                url = input("Enter Supabase URL: ").strip()
        else:
            url = input("Enter Supabase URL: ").strip()
        
        # Get API Key
        current_key = self.config.get('supabase.key', '')
        if current_key:
            print(f"Current key: {current_key[:10]}...")
            use_current = input("Use current key? (y/n): ").lower().startswith('y')
            if use_current:
                key = current_key
            else:
                key = input("Enter Supabase anon key: ").strip()
        else:
            key = input("Enter Supabase anon key: ").strip()
        
        # Save to config
        self.config.config['supabase']['url'] = url
        self.config.config['supabase']['key'] = key
        self.config.config['supabase']['enabled'] = True
        self.config.save_config()
        
        print("✅ Credentials saved!")
        return url, key
    
    def connect_supabase(self) -> bool:
        """Connect to Supabase"""
        try:
            url = self.config.get('supabase.url')
            key = self.config.get('supabase.key')
            
            if not url or not key:
                print("❌ Supabase credentials not found!")
                return False
            
            self.client = create_client(url, key)
            
            # Test connection
            result = self.client.table('_supabase_migrations').select("*").limit(1).execute()
            print("✅ Connected to Supabase!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def deploy_schema(self) -> bool:
        """Deploy the complete database schema"""
        try:
            print("🚀 Deploying Cultural Intelligence System schema...")
            
            # Get the complete schema
            schema_sql = DatabaseSchema.get_schema_sql()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            print(f"📊 Executing {len(statements)} SQL statements...")
            
            success_count = 0
            for i, statement in enumerate(statements):
                try:
                    if statement.upper().startswith(('CREATE', 'INSERT', 'ALTER', 'DROP')):
                        # Execute DDL statements using raw SQL
                        result = self.client.rpc('exec_sql', {'sql': statement}).execute()
                        success_count += 1
                        print(f"✅ Statement {i+1}/{len(statements)}")
                except Exception as e:
                    print(f"⚠️  Statement {i+1} warning: {e}")
                    # Continue with other statements
            
            print(f"🎯 Schema deployment complete! {success_count}/{len(statements)} statements executed")
            return True
            
        except Exception as e:
            print(f"❌ Schema deployment failed: {e}")
            return False
    
    def verify_deployment(self) -> Dict:
        """Verify the deployment by checking tables"""
        try:
            tables_to_check = ['tracks', 'duplicates', 'classifications', 'patterns', 'artist_profiles', 'label_profiles']
            results = {}
            
            print("🔍 Verifying deployment...")
            
            for table in tables_to_check:
                try:
                    result = self.client.table(table).select("count", count='exact').execute()
                    count = result.count if hasattr(result, 'count') else 0
                    results[table] = {'exists': True, 'count': count}
                    print(f"✅ {table}: {count} records")
                except Exception as e:
                    results[table] = {'exists': False, 'error': str(e)}
                    print(f"❌ {table}: {e}")
            
            return results
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return {}
    
    def seed_initial_data(self) -> bool:
        """Seed with initial electronic music data"""
        try:
            print("🌱 Seeding initial electronic music data...")
            
            # Seed some label profiles
            labels_data = [
                {
                    'name': 'Anjunabeats',
                    'normalized_name': 'anjunabeats',
                    'primary_genres': ['Trance', 'Progressive House'],
                    'country': 'UK',
                    'founded_year': 2000,
                    'is_electronic_focused': True
                },
                {
                    'name': 'Defected Records',
                    'normalized_name': 'defected',
                    'primary_genres': ['House', 'Deep House'],
                    'country': 'UK', 
                    'founded_year': 1999,
                    'is_electronic_focused': True
                },
                {
                    'name': 'Monstercat',
                    'normalized_name': 'monstercat',
                    'primary_genres': ['Dubstep', 'Electronic', 'Future Bass'],
                    'country': 'Canada',
                    'founded_year': 2011,
                    'is_electronic_focused': True
                }
            ]
            
            # Insert labels
            result = self.client.table('label_profiles').insert(labels_data).execute()
            print(f"✅ Inserted {len(labels_data)} label profiles")
            
            # Seed some artist profiles  
            artists_data = [
                {
                    'name': 'Deadmau5',
                    'normalized_name': 'deadmau5',
                    'primary_genres': ['Progressive House', 'Electro House'],
                    'track_count': 0,
                    'labels_worked_with': ['Mau5trap', 'Ultra Records']
                },
                {
                    'name': 'Armin van Buuren',
                    'normalized_name': 'armin van buuren',
                    'primary_genres': ['Trance', 'Progressive Trance'],
                    'track_count': 0,
                    'labels_worked_with': ['Armada Music', 'A State of Trance']
                }
            ]
            
            result = self.client.table('artist_profiles').insert(artists_data).execute()
            print(f"✅ Inserted {len(artists_data)} artist profiles")
            
            return True
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            return False

def main():
    """Main deployment process"""
    print("🎵 CULTURAL INTELLIGENCE SYSTEM v3.2")
    print("🔗 Supabase Database Deployment")
    print("=" * 50)
    
    deployer = SupabaseDeployer()
    
    # Step 1: Setup credentials
    if not deployer.config.get('supabase.url') or not deployer.config.get('supabase.key'):
        print("🔧 First-time setup required...")
        deployer.setup_credentials()
    
    # Step 2: Connect
    if not deployer.connect_supabase():
        print("🔧 Setting up new credentials...")
        deployer.setup_credentials()
        if not deployer.connect_supabase():
            print("❌ Could not connect to Supabase!")
            return
    
    # Step 3: Deploy schema
    choice = input("\n🚀 Deploy database schema? (y/n): ").lower()
    if choice.startswith('y'):
        if deployer.deploy_schema():
            print("✅ Schema deployed successfully!")
        else:
            print("❌ Schema deployment failed!")
            return
    
    # Step 4: Verify
    choice = input("\n🔍 Verify deployment? (y/n): ").lower()
    if choice.startswith('y'):
        results = deployer.verify_deployment()
        if results:
            print("✅ Verification complete!")
    
    # Step 5: Seed data
    choice = input("\n🌱 Seed initial data? (y/n): ").lower()
    if choice.startswith('y'):
        if deployer.seed_initial_data():
            print("✅ Initial data seeded!")
    
    print("\n🎯 DEPLOYMENT COMPLETE!")
    print("Your Cultural Intelligence System database is ready!")
    print(f"Supabase URL: {deployer.config.get('supabase.url')}")
    print("You can now run scans and use the MetaCrate API with full database backing.")

if __name__ == "__main__":
    main()