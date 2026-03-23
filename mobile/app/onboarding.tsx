import { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SEEDS } from '@/constants/masterData';
import { useGrowingStore } from '@/store/growingStore';
import type { Seed } from '@/types';

const ONBOARDING_KEY = 'onboarding_completed';

type Step = 'welcome' | 'select_seed' | 'plant';

export default function OnboardingScreen() {
  const [step, setStep] = useState<Step>('welcome');
  const [selectedSeed, setSelectedSeed] = useState<Seed | null>(null);
  const { plantSeed } = useGrowingStore();

  const handleStart = () => setStep('select_seed');

  const handleSeedSelect = (seed: Seed) => setSelectedSeed(seed);

  const handlePlant = async () => {
    if (!selectedSeed) return;
    plantSeed(selectedSeed.id);
    await AsyncStorage.setItem(ONBOARDING_KEY, 'true');
    router.replace('/');
  };

  if (step === 'welcome') {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.center}>
          <Text style={styles.mainEmoji}>🌱</Text>
          <Text style={styles.appName}>タネとキッチン</Text>
          <Text style={styles.tagline}>伝説の食材を育て、{'\n'}料理を解放しよう</Text>
          <Text style={styles.desc}>
            種を植えて、水をあげて、収穫する。{'\n'}
            あなただけのキッチンを育てよう。
          </Text>
          <TouchableOpacity style={styles.primaryButton} onPress={handleStart}>
            <Text style={styles.primaryButtonText}>はじめる</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  if (step === 'select_seed') {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.stepTitle}>最初の種を選ぼう</Text>
          <Text style={styles.stepSubtitle}>育ててみたい食材を1つ選んでください</Text>
          {SEEDS.map((seed) => (
            <TouchableOpacity
              key={seed.id}
              style={[styles.seedCard, selectedSeed?.id === seed.id && styles.seedCardSelected]}
              onPress={() => handleSeedSelect(seed)}
            >
              <Text style={styles.seedEmoji}>🌱</Text>
              <View style={styles.seedInfo}>
                <Text style={styles.seedName}>{seed.name}</Text>
                <Text style={styles.seedDesc}>{seed.description}</Text>
                <Text style={styles.seedTime}>⏱ 約{seed.grow_hours}時間で収穫</Text>
              </View>
              {selectedSeed?.id === seed.id && <Text style={styles.checkmark}>✅</Text>}
            </TouchableOpacity>
          ))}
          <TouchableOpacity
            style={[styles.primaryButton, !selectedSeed && styles.primaryButtonDisabled]}
            onPress={() => selectedSeed && setStep('plant')}
            disabled={!selectedSeed}
          >
            <Text style={styles.primaryButtonText}>この種を選ぶ</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.center}>
        <Text style={styles.mainEmoji}>{selectedSeed ? '🌱' : '❓'}</Text>
        <Text style={styles.stepTitle}>植えましょう！</Text>
        <Text style={styles.stepSubtitle}>
          {selectedSeed?.name}の種を土に植えます。{'\n'}
          水をあげて、成長を見守ろう。
        </Text>
        <View style={styles.seedPreview}>
          <Text style={styles.seedPreviewName}>{selectedSeed?.name}</Text>
          <Text style={styles.seedPreviewDesc}>{selectedSeed?.description}</Text>
        </View>
        <TouchableOpacity style={styles.plantButton} onPress={handlePlant}>
          <Text style={styles.plantButtonText}>🌱 植える</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  scroll: { padding: 24, paddingBottom: 48 },
  mainEmoji: { fontSize: 96, marginBottom: 16 },
  appName: { fontSize: 32, fontWeight: '900', color: '#2D5A27', marginBottom: 8 },
  tagline: { fontSize: 20, fontWeight: '700', color: '#333', textAlign: 'center', lineHeight: 30, marginBottom: 16 },
  desc: { fontSize: 15, color: '#888', textAlign: 'center', lineHeight: 24, marginBottom: 40 },
  stepTitle: { fontSize: 26, fontWeight: '800', color: '#2D5A27', marginBottom: 6 },
  stepSubtitle: { fontSize: 14, color: '#888', textAlign: 'center', lineHeight: 22, marginBottom: 24 },
  seedCard: {
    backgroundColor: '#FFFDF7',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 1,
  },
  seedCardSelected: { borderColor: '#2D5A27' },
  seedEmoji: { fontSize: 36, marginRight: 14 },
  seedInfo: { flex: 1 },
  seedName: { fontSize: 17, fontWeight: '700', color: '#333' },
  seedDesc: { fontSize: 13, color: '#888', marginTop: 2 },
  seedTime: { fontSize: 12, color: '#999', marginTop: 4 },
  checkmark: { fontSize: 24 },
  seedPreview: {
    backgroundColor: '#FFFDF7',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginVertical: 24,
    width: '100%',
  },
  seedPreviewName: { fontSize: 20, fontWeight: '700', color: '#333' },
  seedPreviewDesc: { fontSize: 14, color: '#888', marginTop: 6, textAlign: 'center' },
  primaryButton: {
    backgroundColor: '#2D5A27',
    paddingHorizontal: 48,
    paddingVertical: 16,
    borderRadius: 50,
    marginTop: 12,
    width: '100%',
    alignItems: 'center',
  },
  primaryButtonDisabled: { backgroundColor: '#CCC' },
  primaryButtonText: { color: '#FFF', fontSize: 18, fontWeight: '800' },
  plantButton: {
    backgroundColor: '#F4A623',
    paddingHorizontal: 48,
    paddingVertical: 16,
    borderRadius: 50,
    width: '100%',
    alignItems: 'center',
  },
  plantButtonText: { color: '#FFF', fontSize: 20, fontWeight: '800' },
});
