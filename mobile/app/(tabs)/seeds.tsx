import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { SEEDS } from '@/constants/masterData';
import { useGrowingStore } from '@/store/growingStore';
import type { Seed } from '@/types';

const RARITY_COLOR: Record<string, string> = {
  common: '#78909C',
  uncommon: '#66BB6A',
  rare: '#42A5F5',
  legendary: '#FFA726',
};

const RARITY_LABEL: Record<string, string> = {
  common: 'コモン',
  uncommon: 'アンコモン',
  rare: 'レア',
  legendary: 'レジェンド',
};

export default function SeedsScreen() {
  const { plantSeed, growingItems } = useGrowingStore();

  const handlePlant = (seed: Seed) => {
    const alreadyGrowing = growingItems.some((item) => item.seed_id === seed.id);
    if (alreadyGrowing) {
      Alert.alert('すでに育てています', 'この種はすでに育てています。収穫してから再度植えましょう。');
      return;
    }
    plantSeed(seed.id);
    router.push('/');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>種を選ぶ</Text>
        <Text style={styles.subtitle}>育てたい植物の種を選んでください</Text>

        {SEEDS.map((seed) => {
          const isGrowing = growingItems.some((item) => item.seed_id === seed.id);
          return (
            <TouchableOpacity
              key={seed.id}
              style={[styles.card, isGrowing && styles.cardDisabled]}
              onPress={() => !isGrowing && handlePlant(seed)}
              disabled={isGrowing}
            >
              <Text style={styles.emoji}>🌱</Text>
              <View style={styles.info}>
                <View style={styles.nameRow}>
                  <Text style={styles.name}>{seed.name}</Text>
                  <View style={[styles.rarityBadge, { backgroundColor: RARITY_COLOR[seed.rarity] + '22' }]}>
                    <Text style={[styles.rarityText, { color: RARITY_COLOR[seed.rarity] }]}>
                      {RARITY_LABEL[seed.rarity]}
                    </Text>
                  </View>
                </View>
                <Text style={styles.desc}>{seed.description}</Text>
                <Text style={styles.growTime}>⏱ 約{seed.grow_hours}時間で収穫</Text>
              </View>
              {isGrowing ? (
                <Text style={styles.growingBadge}>育成中</Text>
              ) : (
                <TouchableOpacity
                  style={styles.plantButton}
                  onPress={() => handlePlant(seed)}
                >
                  <Text style={styles.plantButtonText}>植える</Text>
                </TouchableOpacity>
              )}
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  scroll: { padding: 20, paddingBottom: 40 },
  title: { fontSize: 26, fontWeight: '800', color: '#2D5A27', marginBottom: 4 },
  subtitle: { fontSize: 14, color: '#888', marginBottom: 20 },
  card: {
    backgroundColor: '#FFFDF7',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  cardDisabled: { opacity: 0.5 },
  emoji: { fontSize: 36, marginRight: 14 },
  info: { flex: 1 },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 4 },
  name: { fontSize: 17, fontWeight: '700', color: '#333' },
  rarityBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 50 },
  rarityText: { fontSize: 11, fontWeight: '700' },
  desc: { fontSize: 13, color: '#666', marginBottom: 4 },
  growTime: { fontSize: 12, color: '#999' },
  plantButton: {
    backgroundColor: '#2D5A27',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 50,
  },
  plantButtonText: { color: '#FFF', fontSize: 13, fontWeight: '700' },
  growingBadge: { fontSize: 12, color: '#4CAF50', fontWeight: '700' },
});
