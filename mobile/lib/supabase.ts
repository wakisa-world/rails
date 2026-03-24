import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';
import type { Database } from './database.types';

const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

/**
 * Supabase 接続に必要な環境変数が設定されているか確認する。
 * 未設定の場合、DB 操作はスキップして Zustand ローカル状態で動作する。
 */
export const isSupabaseConfigured = (): boolean =>
  SUPABASE_URL.startsWith('https://') && SUPABASE_ANON_KEY.length > 20;

/**
 * Supabase クライアント。
 * 未設定時はプレースホルダー値で初期化するが、
 * 実際のAPI呼び出しは isSupabaseConfigured() でガードすること。
 */
export const supabase = createClient<Database>(
  SUPABASE_URL || 'https://placeholder.supabase.co',
  SUPABASE_ANON_KEY || 'placeholder-anon-key',
  {
    auth: {
      storage: AsyncStorage,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  }
);

/**
 * Supabase への疎通確認。
 * 接続できれば true、失敗（未設定・ネットワークエラー等）なら false を返す。
 * Task1-3 以降のデータ同期開始前に呼び出す。
 */
export async function checkSupabaseConnection(): Promise<boolean> {
  if (!isSupabaseConfigured()) return false;
  try {
    const { error } = await supabase.auth.getSession();
    return error === null;
  } catch {
    return false;
  }
}
