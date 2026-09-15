-- ==============================================================================
-- AI ProjectsHub - User Data SQL Export & Admin Seed File
-- Generated: 2026-09-15
-- 
-- Default Password for All Active Superuser/Staff Accounts below:
-- Password: Admin@123
-- 
-- Available Login Identifiers (Accepts either Username OR Email Address):
-- 1. Username: "Harsh@123"  | Email: "harsh@projectshub.co.in" | Role: Superuser (Staff)
-- 2. Username: "admin"      | Email: ""                       | Role: Superuser (Staff)
-- 3. Username: "QA123"      | Email: "Harsh@cmsminds.com"     | Role: Superuser (Staff)
-- 4. Username: "harsh"      | Email: "Harsh@gmail.com"        | Role: Superuser (Staff)
-- 5. Username: "harsh@123"  | Email: "harshsharmaqa@gmail.com"| Role: Superuser (Staff)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Table Schema (Compatible with SQLite & PostgreSQL)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password" VARCHAR(128) NOT NULL,
    "last_login" DATETIME NULL,
    "is_superuser" BOOLEAN NOT NULL DEFAULT 0,
    "username" VARCHAR(150) NOT NULL UNIQUE,
    "first_name" VARCHAR(150) NOT NULL DEFAULT '',
    "last_name" VARCHAR(150) NOT NULL DEFAULT '',
    "email" VARCHAR(254) NOT NULL DEFAULT '',
    "is_staff" BOOLEAN NOT NULL DEFAULT 0,
    "is_active" BOOLEAN NOT NULL DEFAULT 1,
    "date_joined" DATETIME NOT NULL
);

-- ------------------------------------------------------------------------------
-- 2. SQLite / MySQL Insert & Seed (INSERT OR REPLACE)
--    Password hash corresponds to: Admin@123
-- ------------------------------------------------------------------------------
INSERT OR REPLACE INTO "auth_user" (
    "id", "password", "last_login", "is_superuser", "username", 
    "first_name", "last_name", "email", "is_staff", "is_active", "date_joined"
) VALUES 
(
    1, 
    'pbkdf2_sha256$600000$cjRtLRU4rNXZTupLOWvSXA$zlrUkR/G45QWqSgIaOjaqFnvWKhqfYg0hWa3t+8ptx0=', 
    '2026-09-11 17:08:53.551285', 
    1, 
    'cheta', 
    '', 
    '', 
    '', 
    1, 
    1, 
    '2026-05-07 10:23:09.522000'
),
(
    2, 
    'pbkdf2_sha256$600000$TphWVv92TPXMvbTO4MZNh4$6+FMVrfusfjZJRwzpgi9fRWBrUlMGml+EziFk/e0NuQ=', 
    '2026-05-09 16:45:27.633000', 
    1, 
    'che', 
    '', 
    '', 
    '', 
    1, 
    1, 
    '2026-05-07 10:42:31.094000'
),
(
    3, 
    'pbkdf2_sha256$600000$u8czVlCSKoBdHFJ374s571$48dqxWAUHBOEV+asLLx0hRohvFDZ17WM6Pj/h/Ouegs=', 
    '2026-06-23 18:11:31.037000', 
    1, 
    'a', 
    '', 
    '', 
    'a@gmail.com', 
    1, 
    1, 
    '2026-05-08 16:35:19.335000'
),
(
    4, 
    'pbkdf2_sha256$600000$xr2bU6Ieh0NqfceieXXZDw$WHtrbrzwXBgjWZPp4nQ+0jriW9ZYqNubjLE7XRnCKBQ=', 
    '2026-09-09 03:05:52.313000', 
    1, 
    'admin', 
    '', 
    '', 
    '', 
    1, 
    1, 
    '2026-08-15 11:53:33.230000'
),
(
    5, 
    'pbkdf2_sha256$600000$agS6MHla8cscwblFeaYif9$Nne0BwaQxchA+tFaU9AwtYfo3leCHlVrdyBAIjlYyhY=', 
    '2026-09-08 18:29:37.053000', 
    1, 
    'harsh', 
    '', 
    '', 
    'Harsh@gmail.com', 
    1, 
    1, 
    '2026-09-05 06:48:39.000000'
),
(
    6, 
    'pbkdf2_sha256$600000$hvtGyS2CnVm6vhFyiymB0b$amb8g/zOm/Jgwb4E2EHIN9sZP9/PGWe0sxKWlAJ7HKE=', 
    '2026-09-12 04:32:29.482264', 
    1, 
    'harsh@123', 
    '', 
    '', 
    'harshsharmaqa@gmail.com', 
    1, 
    1, 
    '2026-09-10 11:09:30.580900'
),
(
    7, 
    'pbkdf2_sha256$600000$H9loINiK3jjQ3OF5nhsJuo$pcsC7TPHUslXxeQc1Y3m6miirqxa+Cs/xRcoeKfblAg=', 
    NULL, 
    1, 
    'Harsh@123', 
    '', 
    '', 
    'harsh@projectshub.co.in', 
    1, 
    1, 
    '2026-09-15 12:07:37.023815'
),
(
    8, 
    'pbkdf2_sha256$600000$b0A24WdpJBsvUzJ24qsLaG$09ksofxf0sBV2qX80QmY6EciIm3j3VefxaLE7OKSyDI=', 
    NULL, 
    1, 
    'QA123', 
    '', 
    '', 
    'Harsh@cmsminds.com', 
    1, 
    1, 
    '2026-09-15 12:51:11.773005'
);

-- ------------------------------------------------------------------------------
-- 3. Quick Password Reset Statements (Password: Admin@123)
--    Works on both SQLite and PostgreSQL
-- ------------------------------------------------------------------------------
-- Reset primary admin account
UPDATE "auth_user"
SET 
    "password" = 'pbkdf2_sha256$600000$xr2bU6Ieh0NqfceieXXZDw$WHtrbrzwXBgjWZPp4nQ+0jriW9ZYqNubjLE7XRnCKBQ=',
    "is_staff" = 1,
    "is_superuser" = 1,
    "is_active" = 1
WHERE "username" IN ('Harsh@123', 'admin', 'QA123', 'harsh', 'harsh@123');

-- ------------------------------------------------------------------------------
-- 4. PostgreSQL Upsert Syntax (Optional for production Postgres deployment)
-- ------------------------------------------------------------------------------
/*
INSERT INTO auth_user (username, email, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
VALUES ('Harsh@123', 'harsh@projectshub.co.in', 'pbkdf2_sha256$600000$xr2bU6Ieh0NqfceieXXZDw$WHtrbrzwXBgjWZPp4nQ+0jriW9ZYqNubjLE7XRnCKBQ=', TRUE, TRUE, TRUE, NOW(), '', '')
ON CONFLICT (username) DO UPDATE 
SET password = EXCLUDED.password, is_staff = TRUE, is_superuser = TRUE, is_active = TRUE;
*/
