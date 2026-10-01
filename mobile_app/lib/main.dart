import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'core/network/api_client.dart';
import 'features/create/screens/create_look_screen.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/history/screens/history_screen.dart';

void main() {
  runApp(const AIBeautyStudioApp());
}

class AIBeautyStudioApp extends StatelessWidget {
  const AIBeautyStudioApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final apiClient = ApiClient();

    return MaterialApp(
      title: 'AI Beauty Studio',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: MainNavigationContainer(apiClient: apiClient),
    );
  }
}

class MainNavigationContainer extends StatefulWidget {
  final ApiClient apiClient;

  const MainNavigationContainer({Key? key, required this.apiClient}) : super(key: key);

  @override
  State<MainNavigationContainer> createState() => _MainNavigationContainerState();
}

class _MainNavigationContainerState extends State<MainNavigationContainer> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final screens = [
      CreateLookScreen(apiClient: widget.apiClient),
      HistoryScreen(apiClient: widget.apiClient),
      LoginScreen(apiClient: widget.apiClient),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: AppTheme.pinkPrimary,
        unselectedItemColor: AppTheme.mutedGrey,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.auto_awesome),
            label: 'Create',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: 'My Looks',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Account',
          ),
        ],
      ),
    );
  }
}
