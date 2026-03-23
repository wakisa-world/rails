import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router } from 'expo-router';
import { useGrowingStore } from '@/store/growingStore';
import { SEEDS, calcGrowthStage, STAGE_EMOJI } from '@/constants/masterData';

const STAGE_LABEL = {
  seed: '発芽待ち',
  sprout: '発芽中',
  growing: '成長中',
  ready: '収穫できます！',
};

export default function GrowDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { growingItems, careItem, harvestItem } = useGrowingStore();

  const item = growingItems.find((g) => g.id === id);
  if (!item) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.notFound}>育成データが見つかりません</Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.backLink}>← 戻る</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  const seed = SEEDS.find((s) => s.id === item.seed_id)!;
  const { stage, progressRatio, isHarvestable } = calcGrowthStage(item.planted_at, seed.grow_hours);

  const handleCare = () => {
    careItem(item.id);
    Alert.alert('ケアしました ✨', `${seed.name}が喜んでいます！`);
  };

  const handleHarvest = () => {
    harvestItem(item.id);
    router.replace(`/harvest/${item.id}`);
  };

  const canCare = !item.last_cared_at ||
    Date.now() - new Date(item.last_cared_at).getTime() > 1000 * 60 * 60; // 1時間に1回

  const elapsedHours = (Date.now() - new Date(item.planted_at).getTime()) / 1000 / 60 / 60;
  const remainingHours = Math.max(0, seed.grow_hours - elapsedHours);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>← 戻る</Text>
        </TouchableOpacity>

        {/* メインビジュアル */}
        <View style={styles.visualSection}>
          <Text style={styles.mainEmoji}>{STAGE_EMOJI[stage]}</Text>
          <Text style={styles.stageName}>{seed.name}</Text>
          <View style={[styles.stageBadge, isHarvestable && styles.stageBadgeReady]}>
            <Text style={[styles.stageLabel, isHarvestable && styles.stageLabelReady]}>
              {STAGE_LABEL[stage]}
            </Text>
          </View>
        </View>

        {/* 成長バー */}
        <View style={styles.progressSection}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${Math.round(progressRatio * 100)}%` },
                isHarvestable && styles.progressFillReady,
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {isHarvestable
              ? '収穫タイミングです！'
              : `あと約 ${remainingHours.toFixed(1)} 時間`}
          </Text>
        </View>

        {/* ステータス */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{item.care_count}</Text>
            <Text style={styles.statLabel}>ケア回数</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{Math.round(progressRatio * 100)}%</Text>
            <Text style={styles.statLabel}>成長度</Text>
          </View>
        </View>

        {/* アクションボタン */}
        {isHarvestable ? (
          <TouchableOpacity style={styles.harvestButton} onPress={handleHarvest}>
            <Text style={styles.harvestButtonText}>🎉 収穫する</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={[styles.careButton, !canCare && styles.careButtonDisabled]}
            onPress={handleCare}
            disabled={!canCare}
          >
            <Text style={styles.careButtonText}>
              {canCare ? '💧 ケアする' : '次のケアまで少し待とう'}
            </Text>
          </TouchableOpacity>
        )}

        <Text style={styles.seedDesc}>{seed.description}</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  scroll: { padding: 20, paddingBottom: 40 },
  backBtn: { marginBottom: 16 },
  backText: { fontSize: 16, color: '#2D5A27', fontWeight: '600' },
  visualSection: { alignItems: 'center', paddingVertical: 32 },
  mainEmoji: { fontSize: 100 },
  stageName: { fontSize: 26, fontWeight: '800', color: '#333', marginTop: 12 },
  stageBadge: {
    marginTop: 8,
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 50,
  },
  stageBadgeReady: { backgroundColor: '#FFF3E0' },
  stageLabel: { fontSize: 14, fontWeight: '700', color: '#4CAF50' },
  stageLabelReady: { color: '#F4A623' },
  progressSection: { marginBottom: 20 },
  progressBar: {
    height: 14,
    backgroundColor: '#E8E0D0',
    borderRadius: 7,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: { height: '100%', backgroundColor: '#4CAF50', borderRadius: 7 },
  progressFillReady: { backgroundColor: '#F4A623' },
  progressText: { fontSize: 13, color: '#666', textAlign: 'center' },
  statsRow: {
    flexDirection: 'row',
    backgroundColor: '#FFFDF7',
    borderRadius: 14,
    padding: 16,
    marginBottom: 20,
    gap: 0,
  },
  statItem: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 28, fontWeight: '800', color: '#2D5A27' },
  statLabel: { fontSize: 12, color: '#888', marginTop: 2 },
  harvestButton: {
    backgroundColor: '#F4A623',
    paddingVertical: 18,
    borderRadius: 50,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#F4A623',
    shadowOpacity: 0.4,
    shadowRadius: 10,
    elevation: 4,
  },
  harvestButtonText: { color: '#FFF', fontSize: 20, fontWeight: '800' },
  careButton: {
    backgroundColor: '#2D5A27',
    paddingVertical: 16,
    borderRadius: 50,
    alignItems: 'center',
    marginBottom: 16,
  },
  careButtonDisabled: { backgroundColor: '#CCC' },
  careButtonText: { color: '#FFF', fontSize: 17, fontWeight: '700' },
  seedDesc: { fontSize: 14, color: '#888', textAlign: 'center', lineHeight: 22 },
  notFound: { fontSize: 16, color: '#888', textAlign: 'center', marginTop: 60 },
  backLink: { fontSize: 16, color: '#2D5A27', textAlign: 'center', marginTop: 16 },
});
