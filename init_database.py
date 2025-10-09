#!/usr/bin/env python3
"""
Database initialization script
Creates tables and adds demo user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, User
from app.auth import get_password_hash
from sqlalchemy.orm import Session

def create_tables():
    """Create all database tables"""
    print("🔧 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")

def create_demo_user():
    """Create demo user"""
    print("👤 创建演示用户...")
    
    db = SessionLocal()
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.username == "demo").first()
        if existing_user:
            print("ℹ️  演示用户已存在")
            return
        
        # Create demo user
        demo_user = User(
            username="demo",
            email="demo@example.com",
            hashed_password=get_password_hash("demo123"),
            first_name="演示",
            last_name="用户",
            organization="环境科学研究院",
            is_active=True,
            is_verified=True
        )
        
        db.add(demo_user)
        db.commit()
        print("✅ 演示用户创建成功")
        print("   用户名: demo")
        print("   密码: demo123")
        print("   邮箱: demo@example.com")
        
    except Exception as e:
        print(f"❌ 创建演示用户失败: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 初始化数据库...")
    print("=" * 50)
    
    try:
        # Create tables
        create_tables()
        
        # Create demo user
        create_demo_user()
        
        print("=" * 50)
        print("🎉 数据库初始化完成！")
        print("")
        print("📋 现在您可以：")
        print("   1. 使用演示账户登录 (demo/demo123)")
        print("   2. 注册新用户账户")
        print("   3. 所有用户数据将保存到数据库中")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()