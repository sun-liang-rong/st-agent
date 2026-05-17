"""数据库初始化脚本"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import get_settings

def init_database():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查 users 表是否存在
        result = conn.execute(text("SHOW TABLES LIKE 'users'"))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            # 检查表结构
            result = conn.execute(text("DESCRIBE users"))
            columns = [col[0] for col in result.fetchall()]
            
            # 如果缺少必要字段，添加缺失字段
            required_columns = ['id', 'username', 'email', 'hashed_password', 'full_name', 'is_active', 'is_superuser', 'created_at', 'updated_at']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"缺少字段: {missing_columns}，正在添加...")
                
                # 先检查并删除外键约束
                result = conn.execute(text("SELECT TABLE_NAME, CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_NAME = 'users'"))
                constraints = result.fetchall()
                for table_name, constraint_name in constraints:
                    print(f"删除外键约束: {constraint_name}")
                    conn.execute(text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}"))
                
                # 添加缺失的字段
                if 'email' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(100)"))
                if 'hashed_password' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"))
                if 'full_name' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(100)"))
                if 'is_active' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                if 'is_superuser' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE"))
                if 'created_at' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                if 'updated_at' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP"))
                
                # 添加唯一索引
                conn.execute(text("ALTER TABLE users ADD UNIQUE KEY username_unique (username)"))
                conn.execute(text("ALTER TABLE users ADD UNIQUE KEY email_unique (email)"))
                
                conn.commit()
                print("字段添加成功")
            else:
                print("用户表结构完整")
        else:
            # 创建 users 表
            create_table_sql = """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                is_superuser BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            conn.execute(text(create_table_sql))
            conn.commit()
            print("用户表创建成功")
    
    engine.dispose()

if __name__ == "__main__":
    init_database()