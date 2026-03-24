/**
 * Supabase が自動生成する Database 型のフォーマットに合わせた手動型定義。
 * テーブル構成は Task 0-4 のデータ設計に準拠。
 *
 * 将来的には `npx supabase gen types typescript` で自動生成に切り替え可能。
 */

export type Database = {
  public: {
    Tables: {
      // ============================================================
      // マスター系
      // ============================================================
      seeds: {
        Row: {
          id: string;
          name: string;
          description: string;
          emoji: string;
          rarity: 'common' | 'uncommon' | 'rare' | 'legendary';
          grow_hours: number;
          ingredient_id: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['seeds']['Row'], 'created_at'>;
        Update: Partial<Database['public']['Tables']['seeds']['Insert']>;
      };

      ingredients: {
        Row: {
          id: string;
          name: string;
          description: string;
          emoji: string;
          rarity: 'common' | 'uncommon' | 'rare' | 'legendary';
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['ingredients']['Row'], 'created_at'>;
        Update: Partial<Database['public']['Tables']['ingredients']['Insert']>;
      };

      recipes: {
        Row: {
          id: string;
          name: string;
          description: string;
          emoji: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['recipes']['Row'], 'created_at'>;
        Update: Partial<Database['public']['Tables']['recipes']['Insert']>;
      };

      recipe_ingredients: {
        Row: {
          id: string;
          recipe_id: string;
          ingredient_id: string;
        };
        Insert: Omit<Database['public']['Tables']['recipe_ingredients']['Row'], 'id'>;
        Update: Partial<Database['public']['Tables']['recipe_ingredients']['Insert']>;
      };

      mission_definitions: {
        Row: {
          id: string;
          title: string;
          description: string;
          type: 'daily' | 'one_time';
          target_count: number;
          reward_type: 'seed' | 'experience';
          reward_value: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['mission_definitions']['Row'], 'created_at'>;
        Update: Partial<Database['public']['Tables']['mission_definitions']['Insert']>;
      };

      // ============================================================
      // ユーザー系
      // ============================================================
      users: {
        Row: {
          id: string; // auth.users.id と一致
          display_name: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'created_at'>;
        Update: Partial<Database['public']['Tables']['users']['Insert']>;
      };

      growing_items: {
        Row: {
          id: string;
          user_id: string;
          seed_id: string;
          planted_at: string;
          last_cared_at: string | null;
          care_count: number;
          stage: 'seed' | 'sprout' | 'growing' | 'ready';
          is_harvestable: boolean;
          harvested_at: string | null;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['growing_items']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['growing_items']['Insert']>;
      };

      user_ingredients: {
        Row: {
          id: string;
          user_id: string;
          ingredient_id: string;
          count: number;
          first_obtained_at: string;
        };
        Insert: Omit<Database['public']['Tables']['user_ingredients']['Row'], 'id'>;
        Update: Partial<Database['public']['Tables']['user_ingredients']['Insert']>;
      };

      user_recipes: {
        Row: {
          id: string;
          user_id: string;
          recipe_id: string;
          unlocked_at: string;
        };
        Insert: Omit<Database['public']['Tables']['user_recipes']['Row'], 'id'>;
        Update: Partial<Database['public']['Tables']['user_recipes']['Insert']>;
      };

      user_missions: {
        Row: {
          id: string;
          user_id: string;
          mission_id: string;
          progress: number;
          completed_at: string | null;
          reset_at: string | null;
        };
        Insert: Omit<Database['public']['Tables']['user_missions']['Row'], 'id'>;
        Update: Partial<Database['public']['Tables']['user_missions']['Insert']>;
      };

      user_profile_stats: {
        Row: {
          user_id: string;
          total_harvests: number;
          total_recipes_unlocked: number;
          total_care_count: number;
          current_streak_days: number;
          last_active_at: string;
        };
        Insert: Database['public']['Tables']['user_profile_stats']['Row'];
        Update: Partial<Database['public']['Tables']['user_profile_stats']['Row']>;
      };

      // ============================================================
      // 補助系
      // ============================================================
      share_logs: {
        Row: {
          id: string;
          user_id: string;
          share_type: 'first_harvest' | 'recipe_unlock' | 'encyclopedia_progress' | 'profile';
          shared_at: string;
          metadata: Record<string, unknown> | null;
        };
        Insert: Omit<Database['public']['Tables']['share_logs']['Row'], 'id' | 'shared_at'>;
        Update: never;
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: {
      rarity_type: 'common' | 'uncommon' | 'rare' | 'legendary';
      growth_stage: 'seed' | 'sprout' | 'growing' | 'ready';
      mission_type: 'daily' | 'one_time';
      share_type: 'first_harvest' | 'recipe_unlock' | 'encyclopedia_progress' | 'profile';
    };
  };
};

// ============================================================
// 便利型エイリアス（Task1-3以降で利用）
// ============================================================
type Tables = Database['public']['Tables'];

export type DbGrowingItem = Tables['growing_items']['Row'];
export type DbGrowingItemInsert = Tables['growing_items']['Insert'];
export type DbGrowingItemUpdate = Tables['growing_items']['Update'];

export type DbUserIngredient = Tables['user_ingredients']['Row'];
export type DbUserRecipe = Tables['user_recipes']['Row'];
export type DbUserMission = Tables['user_missions']['Row'];
export type DbUserProfileStats = Tables['user_profile_stats']['Row'];
export type DbShareLog = Tables['share_logs']['Row'];
export type DbShareLogInsert = Tables['share_logs']['Insert'];
