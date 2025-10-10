#!/usr/bin/env python3
"""
Test authentication functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth import get_password_hash, verify_password

def test_password_hashing():
    """Test password hashing and verification"""
    print("🧪 测试密码哈希功能...")
    
    # Test password
    password = "demo123"
    print(f"原始密码: {password}")
    
    try:
        # Hash password
        hashed = get_password_hash(password)
        print(f"哈希密码: {hashed}")
        print(f"哈希长度: {len(hashed)}")
        
        # Verify password
        is_valid = verify_password(password, hashed)
        print(f"密码验证: {'✅ 成功' if is_valid else '❌ 失败'}")
        
        # Test wrong password
        is_wrong = verify_password("wrong_password", hashed)
        print(f"错误密码验证: {'❌ 应该失败' if not is_wrong else '✅ 意外成功'}")
        
        print("✅ 密码哈希测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 密码哈希测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_password_hashing()
    sys.exit(0 if success else 1)