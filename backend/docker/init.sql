-- =============================================
-- Noteworthy 数据库初始化脚本
-- =============================================
-- 此脚本在 PostgreSQL 容器首次启动时自动执行
-- 创建必要的数据库扩展和初始配置

-- 创建 uuid-ossp 扩展（用于生成 UUID）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建 pg_trgm 扩展（用于模糊搜索）
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建全文搜索配置（中文支持）
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = pg_catalog.chinese_zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR nword, word, hword WITH simple;

-- =============================================
-- 注意：数据表结构由 Alembic 迁移脚本管理
-- 执行 `alembic upgrade head` 完成数据库迁移
-- =============================================
