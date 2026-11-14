import { Platform } from "react-native";
import * as Notifications from "expo-notifications";
import type { Alert } from "./types";

// Local notifications work in Expo Go (remote push does not). On web we only show the in-app banner.
let ready = false;

export async function initNotifications(): Promise<boolean> {
  if (Platform.OS === "web") return false;
  Notifications.setNotificationHandler({
    handleNotification: async () => ({ shouldShowBanner: true, shouldShowList: true, shouldPlaySound: true, shouldSetBadge: false }),
  });
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("pond-alerts", {
      name: "Cảnh báo ao", importance: Notifications.AndroidImportance.MAX, vibrationPattern: [0, 300, 200, 300],
    });
  }
  const { status } = await Notifications.requestPermissionsAsync();
  ready = status === "granted";
  return ready;
}

export async function notify(a: Alert) {
  if (!ready) return;
  await Notifications.scheduleNotificationAsync({
    content: { title: a.title, body: a.body, sound: a.severity >= 2 ? "default" : undefined,
               priority: a.severity >= 2 ? Notifications.AndroidNotificationPriority.MAX : Notifications.AndroidNotificationPriority.DEFAULT },
    trigger: Platform.OS === "android" ? { channelId: "pond-alerts" } : null,
  });
}
