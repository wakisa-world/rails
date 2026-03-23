import type { Seed, Ingredient, Recipe, MissionDefinition } from '@/types';

// ============================================================
// 食材マスター（MVP初期：5種）
// ============================================================
export const INGREDIENTS: Ingredient[] = [
  {
    id: 'tomato',
    name: 'トマト',
    description: '太陽の恵みを受けた真っ赤な伝説のトマト。',
    emoji: '🍅',
    rarity: 'common',
  },
  {
    id: 'basil',
    name: 'バジル',
    description: '芳醇な香りを放つ神秘のハーブ。',
    emoji: '🌿',
    rarity: 'common',
  },
  {
    id: 'lettuce',
    name: 'レタス',
    description: '大地の生命力を宿したみずみずしい葉。',
    emoji: '🥬',
    rarity: 'common',
  },
  {
    id: 'carrot',
    name: 'にんじん',
    description: '大地の深くで育った甘みあふれる根菜。',
    emoji: '🥕',
    rarity: 'uncommon',
  },
  {
    id: 'corn',
    name: 'とうもろこし',
    description: '黄金の粒が輝く豊穣の象徴。',
    emoji: '🌽',
    rarity: 'uncommon',
  },
];

// ============================================================
// 種マスター（MVP初期：5種）
// ============================================================
export const SEEDS: Seed[] = [
  {
    id: 'seed_tomato',
    name: 'トマトの種',
    description: '赤く熟したトマトになる小さな命。',
    emoji: '🌱',
    rarity: 'common',
    grow_hours: 8,
    ingredient_id: 'tomato',
  },
  {
    id: 'seed_basil',
    name: 'バジルの種',
    description: '香り高いバジルに育つ神秘の種。',
    emoji: '🌱',
    rarity: 'common',
    grow_hours: 6,
    ingredient_id: 'basil',
  },
  {
    id: 'seed_lettuce',
    name: 'レタスの種',
    description: 'みずみずしいレタスになる小粒の種。',
    emoji: '🌱',
    rarity: 'common',
    grow_hours: 6,
    ingredient_id: 'lettuce',
  },
  {
    id: 'seed_carrot',
    name: 'にんじんの種',
    description: '甘いにんじんになるまで少し時間がかかる。',
    emoji: '🌱',
    rarity: 'uncommon',
    grow_hours: 12,
    ingredient_id: 'carrot',
  },
  {
    id: 'seed_corn',
    name: 'とうもろこしの種',
    description: '大きく育つまでじっくり待とう。',
    emoji: '🌱',
    rarity: 'uncommon',
    grow_hours: 24,
    ingredient_id: 'corn',
  },
];

// ============================================================
// 料理マスター（MVP初期：10種以内）
// ============================================================
export const RECIPES: Recipe[] = [
  {
    id: 'tomato_salad',
    name: 'トマトサラダ',
    description: '新鮮なトマトだけのシンプルサラダ。',
    emoji: '🥗',
    required_ingredient_ids: ['tomato'],
  },
  {
    id: 'basil_salad',
    name: 'バジルサラダ',
    description: 'バジルの香りが広がる爽やかな一品。',
    emoji: '🥗',
    required_ingredient_ids: ['basil'],
  },
  {
    id: 'lettuce_salad',
    name: 'レタスサラダ',
    description: 'シャキシャキのレタスが主役。',
    emoji: '🥗',
    required_ingredient_ids: ['lettuce'],
  },
  {
    id: 'corn_soup',
    name: 'コーンスープ',
    description: '甘みたっぷりのとうもろこしスープ。',
    emoji: '🍵',
    required_ingredient_ids: ['corn'],
  },
  {
    id: 'carrot_soup',
    name: 'にんじんスープ',
    description: '優しい甘みのにんじんポタージュ。',
    emoji: '🍵',
    required_ingredient_ids: ['carrot'],
  },
  {
    id: 'tomato_soup',
    name: 'トマトスープ',
    description: '完熟トマトの旨みが凝縮されたスープ。',
    emoji: '🍲',
    required_ingredient_ids: ['tomato', 'basil'],
  },
  {
    id: 'basil_soup',
    name: 'バジルスープ',
    description: 'バジルが香る緑色の贅沢スープ。',
    emoji: '🍲',
    required_ingredient_ids: ['basil', 'lettuce'],
  },
  {
    id: 'mixed_salad',
    name: 'ミックスサラダ',
    description: '畑の恵みを全部のせた豪華サラダ。',
    emoji: '🥗',
    required_ingredient_ids: ['tomato', 'lettuce', 'carrot'],
  },
  {
    id: 'veg_plate',
    name: 'ベジプレート',
    description: '旬野菜を盛り合わせた彩りプレート。',
    emoji: '🍽️',
    required_ingredient_ids: ['tomato', 'basil', 'lettuce', 'carrot'],
  },
  {
    id: 'harvest_plate',
    name: '収穫プレート',
    description: '全ての食材が揃ったときだけ作れる伝説の一皿。',
    emoji: '✨',
    required_ingredient_ids: ['tomato', 'basil', 'lettuce', 'carrot', 'corn'],
  },
];

// ============================================================
// ミッション定義（MVP初期）
// ============================================================
export const MISSION_DEFINITIONS: MissionDefinition[] = [
  {
    id: 'daily_care_1',
    title: '今日のケア',
    description: '育てている植物のケアを1回する',
    type: 'daily',
    target_count: 1,
    reward_type: 'seed',
    reward_value: 'seed_tomato',
  },
  {
    id: 'daily_harvest_1',
    title: '初めての収穫',
    description: '今日1つ収穫する',
    type: 'daily',
    target_count: 1,
    reward_type: 'experience',
    reward_value: '50',
  },
  {
    id: 'one_time_first_harvest',
    title: '初収穫達成',
    description: 'はじめて収穫する',
    type: 'one_time',
    target_count: 1,
    reward_type: 'seed',
    reward_value: 'seed_carrot',
  },
  {
    id: 'one_time_3_ingredients',
    title: '3種コレクター',
    description: '3種類の食材を集める',
    type: 'one_time',
    target_count: 3,
    reward_type: 'seed',
    reward_value: 'seed_corn',
  },
];

// ============================================================
// 成長段階の判定ユーティリティ
// ============================================================
export function calcGrowthStage(
  plantedAt: string,
  growHours: number
): { stage: import('@/types').GrowthStage; progressRatio: number; isHarvestable: boolean } {
  const now = Date.now();
  const planted = new Date(plantedAt).getTime();
  const elapsed = (now - planted) / 1000 / 60 / 60; // hours
  const progressRatio = Math.min(elapsed / growHours, 1);

  let stage: import('@/types').GrowthStage;
  if (progressRatio < 0.25) stage = 'seed';
  else if (progressRatio < 0.6) stage = 'sprout';
  else if (progressRatio < 1.0) stage = 'growing';
  else stage = 'ready';

  return { stage, progressRatio, isHarvestable: progressRatio >= 1.0 };
}

export const STAGE_EMOJI: Record<import('@/types').GrowthStage, string> = {
  seed: '🌱',
  sprout: '🪴',
  growing: '🌿',
  ready: '✨',
};
