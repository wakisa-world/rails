import { View, Text, TouchableOpacity, StyleSheet, Share, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, router } from 'expo-router';
import { useGrowingStore } from '@/store/growingStore';
import { SEEDS, RECIPES, INGREDIENTS } from '@/constants/masterData';

export default function HarvestResultScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { lastHarvestResult, collectedIngredientIds, unlockedRecipeIds } = useGrowingStore();

  // 直前の収穫結果（storeに保持）
  const result = lastHarvestResult;

  if (!result) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.notFound}>収穫データがありません</Text>
        <TouchableOpacity onPress={() => router.replace('/')}>
          <Text style={styles.homeLink}>ホームへ戻る</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  const ingredient = INGREDIENTS.find((i) => i.id === result.ingredientId)!;
  const newlyUnlockedRecipes = RECIPES.filter((r) => result.newlyUnlockedRecipeIds.includes(r.id));

  const handleShare = async () => {
    try {
      await Share.share({
        message: `${ingredient.emoji} ${ingredient.name}を収穫しました！🎉\n${newlyUnlockedRecipes.length > 0 ? `新しい料理「${newlyUnlockedRecipes[0].name}」が解放されました！\n` : ''}#タネとキッチン`,
      });
    } catch {
      // ignore
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll} bounces={false}>
        {/* 収穫演出 */}
        <View style={styles.heroSection}>
          <Text style={styles.confetti}>🎊</Text>
          <Text style={styles.harvestEmoji}>{ingredient.emoji}</Text>
          <Text style={styles.title}>収穫成功！</Text>
          <Text style={styles.ingredientName}>{ingredient.name}</Text>
          <Text style={styles.desc}>{ingredient.description}</Text>
        </View>

        {/* 新規料理解放 */}
        {newlyUnlockedRecipes.length > 0 && (
          <View style={styles.unlockSection}>
            <Text style={styles.unlockTitle}>🍽️ 新しい料理が解放されました！</Text>
            {newlyUnlockedRecipes.map((recipe) => (
              <View key={recipe.id} style={styles.recipeCard}>
                <Text style={styles.recipeEmoji}>{recipe.emoji}</Text>
                <View>
                  <Text style={styles.recipeName}>{recipe.name}</Text>
                  <Text style={styles.recipeDesc}>{recipe.description}</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* コレクション進捗 */}
        <View style={styles.statsSection}>
          <Text style={styles.statsLabel}>
            食材コレクション {collectedIngredientIds.length}/{INGREDIENTS.length} 種
          </Text>
          <Text style={styles.statsLabel}>
            料理コレクション {unlockedRecipeIds.length}/{RECIPES.length} 種
          </Text>
        </View>

        {/* アクションボタン */}
        <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
          <Text style={styles.shareButtonText}>📤 シェアする</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.nextButton} onPress={() => router.replace('/seeds')}>
          <Text style={styles.nextButtonText}>次の種を育てる 🌱</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.homeButton} onPress={() => router.replace('/')}>
          <Text style={styles.homeButtonText}>ホームへ戻る</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFDF7' },
  scroll: { padding: 24, paddingBottom: 48, alignItems: 'center' },
  heroSection: { alignItems: 'center', paddingVertical: 32 },
  confetti: { fontSize: 48, marginBottom: 8 },
  harvestEmoji: { fontSize: 96 },
  title: { fontSize: 32, fontWeight: '900', color: '#2D5A27', marginTop: 12 },
  ingredientName: { fontSize: 22, fontWeight: '700', color: '#333', marginTop: 4 },
  desc: { fontSize: 14, color: '#888', textAlign: 'center', marginTop: 8, lineHeight: 22, paddingHorizontal: 20 },
  unlockSection: {
    backgroundColor: '#FFF8E1',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    marginBottom: 16,
  },
  unlockTitle: { fontSize: 15, fontWeight: '700', color: '#F4A623', marginBottom: 10 },
  recipeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFDF7',
    borderRadius: 12,
    padding: 12,
    gap: 12,
  },
  recipeEmoji: { fontSize: 32 },
  recipeName: { fontSize: 16, fontWeight: '700', color: '#333' },
  recipeDesc: { fontSize: 12, color: '#888', marginTop: 2 },
  statsSection: {
    backgroundColor: '#F5F0E8',
    borderRadius: 14,
    padding: 16,
    width: '100%',
    marginBottom: 24,
    gap: 6,
  },
  statsLabel: { fontSize: 14, color: '#555', textAlign: 'center' },
  shareButton: {
    backgroundColor: '#F4A623',
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 50,
    width: '100%',
    alignItems: 'center',
    marginBottom: 12,
  },
  shareButtonText: { color: '#FFF', fontSize: 17, fontWeight: '800' },
  nextButton: {
    backgroundColor: '#2D5A27',
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 50,
    width: '100%',
    alignItems: 'center',
    marginBottom: 12,
  },
  nextButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  homeButton: {
    paddingVertical: 12,
    width: '100%',
    alignItems: 'center',
  },
  homeButtonText: { color: '#888', fontSize: 15 },
  notFound: { fontSize: 16, color: '#888', textAlign: 'center', marginTop: 60 },
  homeLink: { fontSize: 16, color: '#2D5A27', textAlign: 'center', marginTop: 16 },
});
