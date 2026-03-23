// ============================================================
// マスターデータ型
// ============================================================

export type SeedRarity = 'common' | 'uncommon' | 'rare' | 'legendary';

export interface Seed {
  id: string;
  name: string;
  description: string;
  emoji: string;
  rarity: SeedRarity;
  grow_hours: number; // 収穫までに必要な時間
  ingredient_id: string; // 収穫後に得られる食材ID
}

export interface Ingredient {
  id: string;
  name: string;
  description: string;
  emoji: string;
  rarity: SeedRarity;
}

export interface Recipe {
  id: string;
  name: string;
  description: string;
  emoji: string;
  required_ingredient_ids: string[]; // 解放に必要な食材IDリスト
}

export interface MissionDefinition {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'one_time';
  target_count: number;
  reward_type: 'seed' | 'experience';
  reward_value: string;
}

// ============================================================
// ユーザーデータ型
// ============================================================

export type GrowthStage = 'seed' | 'sprout' | 'growing' | 'ready';

export interface GrowingItem {
  id: string;
  user_id: string;
  seed_id: string;
  seed: Seed;
  planted_at: string; // ISO 8601
  last_cared_at: string | null;
  care_count: number;
  stage: GrowthStage;
  is_harvestable: boolean;
  harvested_at: string | null;
}

export interface UserIngredient {
  id: string;
  user_id: string;
  ingredient_id: string;
  ingredient: Ingredient;
  count: number;
  first_obtained_at: string;
}

export interface UserRecipe {
  id: string;
  user_id: string;
  recipe_id: string;
  recipe: Recipe;
  unlocked_at: string;
}

export interface UserMission {
  id: string;
  user_id: string;
  mission_id: string;
  mission: MissionDefinition;
  progress: number;
  completed_at: string | null;
  reset_at: string | null;
}

export interface UserProfileStats {
  user_id: string;
  total_harvests: number;
  total_recipes_unlocked: number;
  total_care_count: number;
  current_streak_days: number;
  last_active_at: string;
}

export interface User {
  id: string;
  display_name: string;
  created_at: string;
  profile_stats: UserProfileStats;
}
