import { useEffect, useState } from 'react';
import { checkSupabaseConnection, isSupabaseConfigured } from '@/lib/supabase';

type ConnectionStatus = 'unknown' | 'not_configured' | 'connected' | 'error';

interface SupabaseConnectionState {
  status: ConnectionStatus;
  isReady: boolean; // アプリがデータ操作に進んでよい状態か
}

/**
 * Supabase 接続状態を管理するフック。
 *
 * - not_configured : 環境変数未設定 → Zustand ローカルモードで動作
 * - connected      : 接続成功 → Task1-3 以降の DB 同期が有効
 * - error          : 接続失敗 → ローカルモードにフォールバック
 *
 * isReady は常に true を返す（接続状態に関わらずアプリは動く）。
 */
export function useSupabaseConnection(): SupabaseConnectionState {
  const [status, setStatus] = useState<ConnectionStatus>('unknown');

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      setStatus('not_configured');
      if (__DEV__) {
        console.info(
          '[Supabase] 環境変数未設定 → ローカルモード（Zustand）で動作します。\n' +
            '.env.local に EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY を設定してください。'
        );
      }
      return;
    }

    checkSupabaseConnection().then((ok) => {
      const nextStatus: ConnectionStatus = ok ? 'connected' : 'error';
      setStatus(nextStatus);
      if (__DEV__) {
        console.info(`[Supabase] 接続ステータス: ${nextStatus}`);
      }
    });
  }, []);

  return {
    status,
    // 接続状態に関わらずアプリは常に動作可能
    isReady: status !== 'unknown',
  };
}
