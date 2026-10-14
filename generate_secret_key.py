#!/usr/bin/env python
"""
Generate a secure Django SECRET_KEY for production use.
Run: python generate_secret_key.py
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    key = get_random_secret_key()
    print("\n" + "="*70)
    print("🔐 Generated Secure Django SECRET_KEY")
    print("="*70)
    print(f"\n{key}\n")
    print("="*70)
    print("\n⚠️  IMPORTANT:")
    print("   1. Copy this key")
    print("   2. Add it to your production environment variables as SECRET_KEY")
    print("   3. NEVER commit this key to Git")
    print("   4. Use a different key for each environment (dev/staging/prod)")
    print("\n📚 Next Steps:")
    print("   - Railway: Dashboard → Variables → Add SECRET_KEY")
    print("   - Vercel: Settings → Environment Variables → Add SECRET_KEY")
    print("   - Heroku: heroku config:set SECRET_KEY=\"<your-key>\"")
    print("\n" + "="*70 + "\n")
