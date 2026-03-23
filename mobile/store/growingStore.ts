import { create } from 'zustand';
import { SEEDS, INGREDIENTS, RECIPES, calcGrowthStage } from '@/constants/masterData';
import type { GrowingItem } from '@/types';

// 収穫結果（収穫結果画面に渡す）
interface HarvestResult {
  ingredientId: string;
  newlyUnlockedRecipeIds: string[];
}

interface GrowingState {
  // 育成中アイテム
  growingItems: GrowingItem[];
  // 収穫済み食材IDセット
  collectedIngredientIds: string[];
  // 解放済みレシピIDセット
  unlockedRecipeIds: string[];
  // ミッション進捗 { missionId: count }
  missionProgress: Record<string, number>;
  // 累計収穫数
  totalHarvests: number;
  // 直前の収穫結果（収穫結果画面用）
  lastHarvestResult: HarvestResult | null;

  // アクション
  plantSeed: (seedId: string) => void;
  careItem: (itemId: string) => void;
  harvestItem: (itemId: string) => void;
}

let itemIdCounter = 1;

export const useGrowingStore = create<GrowingState>((set, get) => ({
  growingItems: [],
  collectedIngredientIds: [],
  unlockedRecipeIds: [],
  missionProgress: {},
  totalHarvests: 0,
  lastHarvestResult: null,

  plantSeed: (seedId: string) => {
    const seed = SEEDS.find((s) => s.id === seedId);
    if (!seed) return;

    const newItem: GrowingItem = {
      id: `item_${itemIdCounter++}`,
      user_id: 'local_user',
      seed_id: seedId,
      seed,
      planted_at: new Date().toISOString(),
      last_cared_at: null,
      care_count: 0,
      stage: 'seed',
      is_harvestable: false,
      harvested_at: null,
    };

    set((state) => ({
      growingItems: [...state.growingItems, newItem],
    }));
  },

  careItem: (itemId: string) => {
    set((state) => {
      const updatedItems = state.growingItems.map((item) => {
        if (item.id !== itemId) return item;
        const seed = SEEDS.find((s) => s.id === item.seed_id)!;
        const { stage, isHarvestable } = calcGrowthStage(item.planted_at, seed.grow_hours);
        return {
          ...item,
          last_cared_at: new Date().toISOString(),
          care_count: item.care_count + 1,
          stage,
          is_harvestable: isHarvestable,
        };
      });

      // ミッション進捗更新（daily_care_1）
      const newMissionProgress = { ...state.missionProgress };
      newMissionProgress['daily_care_1'] = (newMissionProgress['daily_care_1'] ?? 0) + 1;

      return { growingItems: updatedItems, missionProgress: newMissionProgress };
    });
  },

  harvestItem: (itemId: string) => {
    set((state) => {
      const item = state.growingItems.find((g) => g.id === itemId);
      if (!item) return state;

      const seed = SEEDS.find((s) => s.id === item.seed_id)!;
      const ingredient = INGREDIENTS.find((i) => i.id === seed.ingredient_id)!;

      // 食材追加
      const newCollectedIds = state.collectedIngredientIds.includes(ingredient.id)
        ? state.collectedIngredientIds
        : [...state.collectedIngredientIds, ingredient.id];

      // 解放できる料理を確認
      const allCollectedAfter = newCollectedIds;
      const newlyUnlockedRecipeIds = RECIPES.filter((recipe) => {
        if (state.unlockedRecipeIds.includes(recipe.id)) return false;
        return recipe.required_ingredient_ids.every((id) => allCollectedAfter.includes(id));
      }).map((r) => r.id);

      const newUnlockedRecipeIds = [...state.unlockedRecipeIds, ...newlyUnlockedRecipeIds];

      // 育成リストから削除
      const newGrowingItems = state.growingItems.filter((g) => g.id !== itemId);

      // ミッション進捗更新
      const newMissionProgress = { ...state.missionProgress };
      newMissionProgress['daily_harvest_1'] = (newMissionProgress['daily_harvest_1'] ?? 0) + 1;
      if ((newMissionProgress['one_time_first_harvest'] ?? 0) === 0) {
        newMissionProgress['one_time_first_harvest'] = 1;
      }
      newMissionProgress['one_time_3_ingredients'] = newCollectedIds.length;

      const harvestResult: HarvestResult = {
        ingredientId: ingredient.id,
        newlyUnlockedRecipeIds,
      };

      return {
        growingItems: newGrowingItems,
        collectedIngredientIds: newCollectedIds,
        unlockedRecipeIds: newUnlockedRecipeIds,
        missionProgress: newMissionProgress,
        totalHarvests: state.totalHarvests + 1,
        lastHarvestResult: harvestResult,
      };
    });
  },
}));
