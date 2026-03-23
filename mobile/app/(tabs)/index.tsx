import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useGrowingStore } from '@/store/growingStore';
import { STAGE_EMOJI, calcGrowthStage, SEEDS } from '@/constants/masterData';

export default function HomeScreen() {
  const { growingItems } = useGrowingStore();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <Text style={styles.title}>タネとキッチン</Text>
          <Text style={styles.subtitle}>今日も育てよう</Text>
        </View>

        {growingItems.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyEmoji}>🌱</Text>
            <Text style={styles.emptyTitle}>まだ何も育てていません</Text>
            <Text style={styles.emptyDesc}>種を植えて、育てはじめましょう</Text>
            <TouchableOpacity
              style={styles.primaryButton}
              onPress={() => router.push('/seeds')}
            >
              <Text style={styles.primaryButtonText}>種を選ぶ</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>育てている植物</Text>
            {growingItems.map((item) => {
              const seed = SEEDS.find((s) => s.id === item.seed_id);
              if (!seed) return null;
              const { stage, progressRatio, isHarvestable } = calcGrowthStage(
                item.planted_at,
                seed.grow_hours
              );
              return (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.card, isHarvestable && styles.cardHarvestable]}
                  onPress={() => router.push(`/grow/${item.id}`)}
                >
                  <Text style={styles.cardEmoji}>{STAGE_EMOJI[stage]}</Text>
                  <View style={styles.cardInfo}>
                    <Text style={styles.cardName}>{seed.name}</Text>
                    <View style={styles.progressBar}>
                      <View
                        style={[
                          styles.progressFill,
                          { width: `${Math.round(progressRatio * 100)}%` },
                        ]}
                      />
                    </View>
                    {isHarvestable && (
                      <Text style={styles.harvestBadge}>収穫できます ✨</Text>
                    )}
                  </View>
                  <Text style={styles.cardArrow}>›</Text>
                </TouchableOpacity>
              );
            })}

            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => router.push('/seeds')}
            >
              <Text style={styles.secondaryButtonText}>＋ 新しい種を植える</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  scroll: { padding: 20, paddingBottom: 40 },
  header: { marginBottom: 24 },
  title: { fontSize: 28, fontWeight: '800', color: '#2D5A27', letterSpacing: -0.5 },
  subtitle: { fontSize: 14, color: '#888', marginTop: 4 },
  section: { gap: 12 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#333', marginBottom: 4 },
  card: {
    backgroundColor: '#FFFDF7',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  cardHarvestable: { borderColor: '#F4A623', borderWidth: 2 },
  cardEmoji: { fontSize: 36, marginRight: 14 },
  cardInfo: { flex: 1 },
  cardName: { fontSize: 16, fontWeight: '700', color: '#333', marginBottom: 6 },
  progressBar: {
    height: 6,
    backgroundColor: '#E8E0D0',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: { height: '100%', backgroundColor: '#4CAF50', borderRadius: 3 },
  harvestBadge: { fontSize: 12, color: '#F4A623', fontWeight: '700', marginTop: 4 },
  cardArrow: { fontSize: 24, color: '#CCC', marginLeft: 8 },
  emptyState: { alignItems: 'center', paddingVertical: 60, gap: 12 },
  emptyEmoji: { fontSize: 64 },
  emptyTitle: { fontSize: 20, fontWeight: '700', color: '#333' },
  emptyDesc: { fontSize: 14, color: '#888' },
  primaryButton: {
    backgroundColor: '#2D5A27',
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 50,
    marginTop: 8,
  },
  primaryButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  secondaryButton: {
    borderColor: '#2D5A27',
    borderWidth: 1.5,
    paddingVertical: 12,
    borderRadius: 50,
    alignItems: 'center',
    marginTop: 4,
  },
  secondaryButtonText: { color: '#2D5A27', fontSize: 15, fontWeight: '600' },
});
