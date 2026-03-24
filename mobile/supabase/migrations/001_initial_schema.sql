-- ============================================================
-- タネとキッチン MVP 初期スキーマ
-- Task 0-4 データ設計に基づく
--
-- 実行場所: Supabase ダッシュボード > SQL Editor
-- 実行順序: このファイルを上から順に実行する
-- ============================================================

-- Enum 型定義
CREATE TYPE rarity_type   AS ENUM ('common', 'uncommon', 'rare', 'legendary');
CREATE TYPE growth_stage  AS ENUM ('seed', 'sprout', 'growing', 'ready');
CREATE TYPE mission_type  AS ENUM ('daily', 'one_time');
CREATE TYPE reward_type   AS ENUM ('seed', 'experience');
CREATE TYPE share_type    AS ENUM ('first_harvest', 'recipe_unlock', 'encyclopedia_progress', 'profile');

-- ============================================================
-- マスター系テーブル
-- ============================================================

CREATE TABLE ingredients (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT NOT NULL,
  emoji       TEXT NOT NULL,
  rarity      rarity_type NOT NULL DEFAULT 'common',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE seeds (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  description   TEXT NOT NULL,
  emoji         TEXT NOT NULL,
  rarity        rarity_type NOT NULL DEFAULT 'common',
  grow_hours    INTEGER NOT NULL CHECK (grow_hours > 0),
  ingredient_id TEXT NOT NULL REFERENCES ingredients(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recipes (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT NOT NULL,
  emoji       TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recipe_ingredients (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id     TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  ingredient_id TEXT NOT NULL REFERENCES ingredients(id),
  UNIQUE (recipe_id, ingredient_id)
);

CREATE TABLE mission_definitions (
  id           TEXT PRIMARY KEY,
  title        TEXT NOT NULL,
  description  TEXT NOT NULL,
  type         mission_type NOT NULL,
  target_count INTEGER NOT NULL CHECK (target_count > 0),
  reward_type  reward_type NOT NULL,
  reward_value TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- ユーザー系テーブル
-- ============================================================

-- auth.users と 1:1 対応するプロフィール
CREATE TABLE users (
  id           UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT NOT NULL DEFAULT '農夫さん',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE growing_items (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  seed_id       TEXT NOT NULL REFERENCES seeds(id),
  planted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_cared_at TIMESTAMPTZ,
  care_count    INTEGER NOT NULL DEFAULT 0,
  stage         growth_stage NOT NULL DEFAULT 'seed',
  is_harvestable BOOLEAN NOT NULL DEFAULT FALSE,
  harvested_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_ingredients (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  ingredient_id    TEXT NOT NULL REFERENCES ingredients(id),
  count            INTEGER NOT NULL DEFAULT 1 CHECK (count >= 0),
  first_obtained_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, ingredient_id)
);

CREATE TABLE user_recipes (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  recipe_id   TEXT NOT NULL REFERENCES recipes(id),
  unlocked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, recipe_id)
);

CREATE TABLE user_missions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mission_id  TEXT NOT NULL REFERENCES mission_definitions(id),
  progress    INTEGER NOT NULL DEFAULT 0,
  completed_at TIMESTAMPTZ,
  reset_at    TIMESTAMPTZ,
  UNIQUE (user_id, mission_id)
);

CREATE TABLE user_profile_stats (
  user_id                UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  total_harvests         INTEGER NOT NULL DEFAULT 0,
  total_recipes_unlocked INTEGER NOT NULL DEFAULT 0,
  total_care_count       INTEGER NOT NULL DEFAULT 0,
  current_streak_days    INTEGER NOT NULL DEFAULT 0,
  last_active_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 補助系テーブル
-- ============================================================

CREATE TABLE share_logs (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  share_type share_type NOT NULL,
  shared_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata   JSONB
);

-- ============================================================
-- Row Level Security（RLS）
-- ============================================================

-- 全テーブルで RLS 有効化
ALTER TABLE users               ENABLE ROW LEVEL SECURITY;
ALTER TABLE growing_items       ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ingredients    ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_recipes        ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_missions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profile_stats  ENABLE ROW LEVEL SECURITY;
ALTER TABLE share_logs          ENABLE ROW LEVEL SECURITY;

-- マスターデータは全員読み取り可（書き込みは管理者のみ）
ALTER TABLE seeds               ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingredients         ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes             ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_ingredients  ENABLE ROW LEVEL SECURITY;
ALTER TABLE mission_definitions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "master_data_read_all" ON seeds               FOR SELECT USING (true);
CREATE POLICY "master_data_read_all" ON ingredients         FOR SELECT USING (true);
CREATE POLICY "master_data_read_all" ON recipes             FOR SELECT USING (true);
CREATE POLICY "master_data_read_all" ON recipe_ingredients  FOR SELECT USING (true);
CREATE POLICY "master_data_read_all" ON mission_definitions FOR SELECT USING (true);

-- ユーザーは自分のデータのみ操作可
CREATE POLICY "users_own"              ON users              FOR ALL  USING (auth.uid() = id);
CREATE POLICY "growing_items_own"      ON growing_items      FOR ALL  USING (auth.uid() = user_id);
CREATE POLICY "user_ingredients_own"   ON user_ingredients   FOR ALL  USING (auth.uid() = user_id);
CREATE POLICY "user_recipes_own"       ON user_recipes       FOR ALL  USING (auth.uid() = user_id);
CREATE POLICY "user_missions_own"      ON user_missions      FOR ALL  USING (auth.uid() = user_id);
CREATE POLICY "user_profile_stats_own" ON user_profile_stats FOR ALL  USING (auth.uid() = user_id);
CREATE POLICY "share_logs_own"         ON share_logs         FOR ALL  USING (auth.uid() = user_id);

-- ============================================================
-- 新規ユーザー登録トリガー
-- auth.users にユーザーが作成されたとき、users / user_profile_stats を自動作成
-- ============================================================

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, display_name)
  VALUES (NEW.id, '農夫さん');

  INSERT INTO public.user_profile_stats (user_id)
  VALUES (NEW.id);

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ============================================================
-- 初期マスターデータ投入
-- ============================================================

INSERT INTO ingredients (id, name, description, emoji, rarity) VALUES
  ('tomato',  'トマト',      '太陽の恵みを受けた真っ赤な伝説のトマト。',   '🍅', 'common'),
  ('basil',   'バジル',      '芳醇な香りを放つ神秘のハーブ。',            '🌿', 'common'),
  ('lettuce', 'レタス',      '大地の生命力を宿したみずみずしい葉。',       '🥬', 'common'),
  ('carrot',  'にんじん',    '大地の深くで育った甘みあふれる根菜。',       '🥕', 'uncommon'),
  ('corn',    'とうもろこし', '黄金の粒が輝く豊穣の象徴。',               '🌽', 'uncommon');

INSERT INTO seeds (id, name, description, emoji, rarity, grow_hours, ingredient_id) VALUES
  ('seed_tomato',  'トマトの種',      '赤く熟したトマトになる小さな命。',            '🌱', 'common',   8,  'tomato'),
  ('seed_basil',   'バジルの種',      '香り高いバジルに育つ神秘の種。',              '🌱', 'common',   6,  'basil'),
  ('seed_lettuce', 'レタスの種',      'みずみずしいレタスになる小粒の種。',          '🌱', 'common',   6,  'lettuce'),
  ('seed_carrot',  'にんじんの種',    '甘いにんじんになるまで少し時間がかかる。',    '🌱', 'uncommon', 12, 'carrot'),
  ('seed_corn',    'とうもろこしの種', '大きく育つまでじっくり待とう。',             '🌱', 'uncommon', 24, 'corn');

INSERT INTO recipes (id, name, description, emoji) VALUES
  ('tomato_salad',   'トマトサラダ',    '新鮮なトマトだけのシンプルサラダ。',               '🥗'),
  ('basil_salad',    'バジルサラダ',    'バジルの香りが広がる爽やかな一品。',              '🥗'),
  ('lettuce_salad',  'レタスサラダ',    'シャキシャキのレタスが主役。',                   '🥗'),
  ('corn_soup',      'コーンスープ',    '甘みたっぷりのとうもろこしスープ。',              '🍵'),
  ('carrot_soup',    'にんじんスープ',  '優しい甘みのにんじんポタージュ。',               '🍵'),
  ('tomato_soup',    'トマトスープ',    '完熟トマトの旨みが凝縮されたスープ。',            '🍲'),
  ('basil_soup',     'バジルスープ',    'バジルが香る緑色の贅沢スープ。',                 '🍲'),
  ('mixed_salad',    'ミックスサラダ',  '畑の恵みを全部のせた豪華サラダ。',               '🥗'),
  ('veg_plate',      'ベジプレート',    '旬野菜を盛り合わせた彩りプレート。',             '🍽️'),
  ('harvest_plate',  '収穫プレート',    '全ての食材が揃ったときだけ作れる伝説の一皿。',   '✨');

INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES
  ('tomato_salad',  'tomato'),
  ('basil_salad',   'basil'),
  ('lettuce_salad', 'lettuce'),
  ('corn_soup',     'corn'),
  ('carrot_soup',   'carrot'),
  ('tomato_soup',   'tomato'),
  ('tomato_soup',   'basil'),
  ('basil_soup',    'basil'),
  ('basil_soup',    'lettuce'),
  ('mixed_salad',   'tomato'),
  ('mixed_salad',   'lettuce'),
  ('mixed_salad',   'carrot'),
  ('veg_plate',     'tomato'),
  ('veg_plate',     'basil'),
  ('veg_plate',     'lettuce'),
  ('veg_plate',     'carrot'),
  ('harvest_plate', 'tomato'),
  ('harvest_plate', 'basil'),
  ('harvest_plate', 'lettuce'),
  ('harvest_plate', 'carrot'),
  ('harvest_plate', 'corn');

INSERT INTO mission_definitions (id, title, description, type, target_count, reward_type, reward_value) VALUES
  ('daily_care_1',           '今日のケア',     '育てている植物のケアを1回する', 'daily',    1, 'seed',       'seed_tomato'),
  ('daily_harvest_1',        '今日の収穫',     '今日1つ収穫する',              'daily',    1, 'experience', '50'),
  ('one_time_first_harvest', '初収穫達成',     'はじめて収穫する',             'one_time', 1, 'seed',       'seed_carrot'),
  ('one_time_3_ingredients', '3種コレクター', '3種類の食材を集める',          'one_time', 3, 'seed',       'seed_corn');
