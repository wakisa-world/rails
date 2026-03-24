import { useEffect } from 'react';
import { Stack, router } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useSupabaseConnection } from '@/hooks/useSupabaseConnection';

const ONBOARDING_KEY = 'onboarding_completed';

export default function RootLayout() {
  // Supabase 接続状態を確認（ログ出力のみ、UIには影響しない）
  useSupabaseConnection();

  useEffect(() => {
    checkOnboarding();
  }, []);

  const checkOnboarding = async () => {
    try {
      const completed = await AsyncStorage.getItem(ONBOARDING_KEY);
      if (!completed) {
        router.replace('/onboarding');
      }
    } catch {
      // エラー時はそのままホームへ
    }
  };

  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="grow/[id]" options={{ presentation: 'card' }} />
        <Stack.Screen name="harvest/[id]" options={{ presentation: 'modal' }} />
      </Stack>
    </>
  );
}
