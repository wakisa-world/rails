import { View, Text, ScrollView, TouchableOpacity, Share, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useGrowingStore } from '@/store/growingStore';
import { INGREDIENTS, RECIPES } from '@/constants/masterData';

export default function ProfileScreen() {
  const { collectedIngredientIds, unlockedRecipeIds, totalHarvests } = useGrowingStore();

  const handleShare = async () => {
    try {
      await Share.share({
        message: `タネとキッチンで${totalHarvests}回収穫しました！🌱 食材${collectedIngredientIds.length}/${INGREDIENTS.length}種・料理${unlockedRecipeIds.length}/${RECIPES.length}種をコレクション中！ #タネとキッチン`,
      });
    } catch {
      // ignore
    }
  };

  const progressPercent = Math.round(
    ((collectedIngredientIds.length + unlockedRecipeIds.length) /
      (INGREDIENTS.length + RECIPES.length)) *
      100
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.avatarSection}>
          <Text style={styles.avatar}>🧑‍🌾</Text>
          <Text style={styles.userName}>農夫さん</Text>
        </View>

        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{totalHarvests}</Text>
            <Text style={styles.statLabel}>収穫回数</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {collectedIngredientIds.length}/{INGREDIENTS.length}
            </Text>
            <Text style={styles.statLabel}>食材</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {unlockedRecipeIds.length}/{RECIPES.length}
            </Text>
            <Text style={styles.statLabel}>料理</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{progressPercent}%</Text>
            <Text style={styles.statLabel}>コンプリート</Text>
          </View>
        </View>

        <View style={styles.progressSection}>
          <Text style={styles.progressTitle}>図鑑の進捗</Text>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${progressPercent}%` }]} />
          </View>
          <Text style={styles.progressText}>{progressPercent}% 完成</Text>
        </View>

        <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
          <Text style={styles.shareButtonText}>📤 プロフィールをシェア</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  scroll: { padding: 20, paddingBottom: 40 },
  avatarSection: { alignItems: 'center', paddingVertical: 24 },
  avatar: { fontSize: 72 },
  userName: { fontSize: 20, fontWeight: '700', color: '#333', marginTop: 8 },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: '#FFFDF7',
    borderRadius: 14,
    padding: 16,
    alignItems: 'center',
    width: '47%',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 1,
  },
  statValue: { fontSize: 28, fontWeight: '800', color: '#2D5A27' },
  statLabel: { fontSize: 12, color: '#888', marginTop: 2 },
  progressSection: { marginBottom: 24 },
  progressTitle: { fontSize: 15, fontWeight: '700', color: '#333', marginBottom: 10 },
  progressBar: {
    height: 10,
    backgroundColor: '#E8E0D0',
    borderRadius: 5,
    overflow: 'hidden',
    marginBottom: 6,
  },
  progressFill: { height: '100%', backgroundColor: '#4CAF50', borderRadius: 5 },
  progressText: { fontSize: 13, color: '#666', textAlign: 'right' },
  shareButton: {
    backgroundColor: '#2D5A27',
    paddingVertical: 16,
    borderRadius: 50,
    alignItems: 'center',
  },
  shareButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
});
