import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useGrowingStore } from '@/store/growingStore';
import { INGREDIENTS, RECIPES } from '@/constants/masterData';

export default function EncyclopediaScreen() {
  const { collectedIngredientIds, unlockedRecipeIds } = useGrowingStore();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>図鑑</Text>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            食材 {collectedIngredientIds.length}/{INGREDIENTS.length}
          </Text>
          <View style={styles.grid}>
            {INGREDIENTS.map((ing) => {
              const collected = collectedIngredientIds.includes(ing.id);
              return (
                <View key={ing.id} style={[styles.gridItem, !collected && styles.gridItemLocked]}>
                  <Text style={[styles.gridEmoji, !collected && styles.gridEmojiLocked]}>
                    {collected ? ing.emoji : '❓'}
                  </Text>
                  <Text style={[styles.gridName, !collected && styles.gridNameLocked]}>
                    {collected ? ing.name : '???'}
                  </Text>
                </View>
              );
            })}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            料理 {unlockedRecipeIds.length}/{RECIPES.length}
          </Text>
          {RECIPES.map((recipe) => {
            const unlocked = unlockedRecipeIds.includes(recipe.id);
            return (
              <View key={recipe.id} style={[styles.recipeCard, !unlocked && styles.recipeCardLocked]}>
                <Text style={[styles.recipeEmoji, !unlocked && styles.lockedText]}>
                  {unlocked ? recipe.emoji : '🔒'}
                </Text>
                <View style={styles.recipeInfo}>
                  <Text style={[styles.recipeName, !unlocked && styles.lockedText]}>
                    {unlocked ? recipe.name : '???'}
                  </Text>
                  {unlocked && (
                    <Text style={styles.recipeDesc}>{recipe.description}</Text>
                  )}
                </View>
              </View>
            );
          })}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  scroll: { padding: 20, paddingBottom: 40 },
  title: { fontSize: 26, fontWeight: '800', color: '#2D5A27', marginBottom: 20 },
  section: { marginBottom: 28 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#333', marginBottom: 12 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  gridItem: {
    backgroundColor: '#FFFDF7',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    width: '30%',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  gridItemLocked: { backgroundColor: '#EEE' },
  gridEmoji: { fontSize: 32, marginBottom: 4 },
  gridEmojiLocked: { opacity: 0.4 },
  gridName: { fontSize: 11, fontWeight: '600', color: '#333', textAlign: 'center' },
  gridNameLocked: { color: '#BBB' },
  recipeCard: {
    backgroundColor: '#FFFDF7',
    borderRadius: 14,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  recipeCardLocked: { backgroundColor: '#F0F0F0' },
  recipeEmoji: { fontSize: 32, marginRight: 12 },
  recipeInfo: { flex: 1 },
  recipeName: { fontSize: 16, fontWeight: '700', color: '#333' },
  recipeDesc: { fontSize: 12, color: '#888', marginTop: 2 },
  lockedText: { color: '#BBB' },
});
