import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MISSION_DEFINITIONS } from '@/constants/masterData';
import { useGrowingStore } from '@/store/growingStore';

export default function MissionsScreen() {
  const { missionProgress } = useGrowingStore();

  const dailyMissions = MISSION_DEFINITIONS.filter((m) => m.type === 'daily');
  const oneTimeMissions = MISSION_DEFINITIONS.filter((m) => m.type === 'one_time');

  const renderMission = (mission: typeof MISSION_DEFINITIONS[0]) => {
    const progress = missionProgress[mission.id] ?? 0;
    const completed = progress >= mission.target_count;
    return (
      <View key={mission.id} style={[styles.card, completed && styles.cardCompleted]}>
        <View style={styles.cardLeft}>
          <Text style={styles.missionTitle}>{mission.title}</Text>
          <Text style={styles.missionDesc}>{mission.description}</Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${Math.min((progress / mission.target_count) * 100, 100)}%`,
                  backgroundColor: completed ? '#4CAF50' : '#F4A623',
                },
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {Math.min(progress, mission.target_count)} / {mission.target_count}
          </Text>
        </View>
        {completed && <Text style={styles.completedBadge}>✅</Text>}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>ミッション</Text>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>デイリー</Text>
          {dailyMissions.map(renderMission)}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>達成目標</Text>
          {oneTimeMissions.map(renderMission)}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F0E8' },
  scroll: { padding: 20, paddingBottom: 40 },
  title: { fontSize: 26, fontWeight: '800', color: '#2D5A27', marginBottom: 20 },
  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#333', marginBottom: 10 },
  card: {
    backgroundColor: '#FFFDF7',
    borderRadius: 14,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 1,
  },
  cardCompleted: { borderColor: '#4CAF50', borderWidth: 1.5 },
  cardLeft: { flex: 1 },
  missionTitle: { fontSize: 16, fontWeight: '700', color: '#333', marginBottom: 2 },
  missionDesc: { fontSize: 13, color: '#666', marginBottom: 8 },
  progressBar: {
    height: 6,
    backgroundColor: '#E8E0D0',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 4,
  },
  progressFill: { height: '100%', borderRadius: 3 },
  progressText: { fontSize: 11, color: '#999' },
  completedBadge: { fontSize: 24, marginLeft: 12 },
});
